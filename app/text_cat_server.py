#!/usr/bin/env python
from flask import Flask, jsonify, request
from celery import Celery
from celery.task.control import inspect
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

import training_routines
import prediction_routines

app = Flask(__name__)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Initialize AWS DynamoDB connection
# If needed, update region and endpoint to reflect the actual
dynamodb = boto3.resource('dynamodb', region_name='us-east-1'
            , endpoint_url="http://dynamodb.us-east-1.amazonaws.com")

table = dynamodb.Table('albert_text_cat')

# A long running task handled asynchronously
@celery.task
def training_task(train_request):
    training_routines.train(app, table, train_request)

# Train a new model
@app.route('/models', methods=['POST'])
def train_model():
    if not (request.json
            and all(par in request.json for par in ['id', 's3bucket', 'training_object'])):
        return jsonify({'error': 'Required parameters not supplied'}), 400

    train_request = {
        'id': request.json['id']
        , 's3bucket': request.json['s3bucket']
        , 'training_object': request.json['training_object']
        , 'spacy_model': request.json.get('spacy_model', "")
        , 'n_texts': request.json.get('n_texts', 2000)
        , 'n_iter': request.json.get('n_iter', 20)
    }

    force_update = request.json.get('force_update', 'False')

    # if model["spacy_model"]:
    #     nlp = spacy.load(model["spacy_model"])  # load existing spaCy model
    # else:
    #     nlp = spacy.blank("en")  # create blank Language class
    
    try:
        if force_update != 'True':  # Train only new models if not explicitly forced
            response = table.query(
                KeyConditionExpression=Key('key').eq('model') & Key('sort').eq(train_request['id'])
            )
            if len(response['Items']) > 0:  # Check if the model already exists
                return jsonify({'error': 'Cannot update existing model. Use force_update:True'}), 400

        table.put_item(
            Item={
                'key': 'model'
                , 'sort': train_request["id"]
                , 'data': json.dumps(train_request)
                , 'status': 'started'
            }
        )
    except Exception as e:
        return jsonify({'error': f"{e}"}), 500

    task = training_task.delay(train_request) # Submit to Celery for queing

    return jsonify({'status': 'model training started', 'task_id': task.id}), 202

# Delete an existing model
@app.route('/models/<string:model_id>', methods=['DELETE'])
def delete_model(model_id):
    try:
        response = table.get_item(
            Key={
                'key': 'model'
                , 'sort': model_id
            }
        )
    except Exception as e:
        return jsonify({'error': f"{e}"}), 500

    # Check for existing model
    if 'Item' in response:
        item = response['Item']
    else:
        return jsonify({'error': 'Requested Model ID does not exist'}), 400

    try:
        response = table.delete_item(
            Key={
                'key': 'model'
                , 'sort': model_id
            }
            , ReturnValues='ALL_OLD'
        )
    except Exception as e:
        return jsonify({'error': f"{e}"}), 500

    return jsonify(response)

# Get list of existing models
@app.route('/models', methods=['GET'])
def get_models():
    try:
        response = table.query(
            KeyConditionExpression=Key('key').eq('model')
        )
    except Exception as e:
        return jsonify({'error': f"{e}"}), 500

    items = response['Items']
    for i, v in enumerate(items):
        items[i]["data"] = json.loads(v["data"])  # Converting string to json
    return jsonify(items)

# Classify an input text
@app.route('/prediction', methods=['GET'])
def get_prediction():
    # Check for data imput correctness
    if not (request.json
            and all(par in request.json for par in ['model_id', 'text'])):
        return jsonify({'error': 'Required parameters not supplied'}), 400

    try:
        prediction_request = {
            'model_id': request.json['model_id']
            , 'text': request.json['text']
            , 'n_top': int(request.json.get('n_top', 5))
        }
    except Exception as e:
        return jsonify({'error': 'Wrong parameters'}), 400

    try:
        response = table.query(
            KeyConditionExpression=Key('key').eq('model') & Key('sort').eq(prediction_request['model_id'])
        )
    except Exception as e:
        return jsonify({'error': f"{e}"}), 500

    if len(response['Items']) == 0:
        return jsonify({'error': 'Model ID does not exist'}), 400

    model = json.loads(response['Items'][0]["data"])
    prediction = prediction_routines.predict(model, prediction_request)
    return jsonify({'prediction_request': prediction_request, 'model': model, 'prediction': prediction})

if __name__ == '__main__':
    app.run(host='0.0.0.0')