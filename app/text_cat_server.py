#!/usr/bin/env python
from flask import Flask, jsonify, request
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from . import training_routines
from . import prediction_routines

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1'
            , endpoint_url="http://dynamodb.us-east-1.amazonaws.com")

table = dynamodb.Table('albert_text_cat')

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
        if force_update != 'True':
            response = table.put_item(
                Item={
                    'key': 'model'
                    , 'sort': train_request["id"]
                    , 'data': json.dumps(train_request)
                }
                , ConditionExpression=Attr("key").not_exists() & Attr("sort").not_exists() 
            )
        else:
            response = table.put_item(
                Item={
                    'key': 'model'
                    , 'sort': train_request["id"]
                    , 'data': json.dumps(train_request)
                }
                , ReturnValues='ALL_OLD'
            )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return jsonify({'error': 'Cannot update existing model. Use force_update:True'}), 400
        return jsonify({'error': f"{e}"}), 500
    except Exception as e:
        return jsonify({'error': f"{e}"}), 500

    training_routines.train(train_request)

    return jsonify(response)

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
        items[i]["data"] = json.loads(v["data"])
    return jsonify(items)

@app.route('/prediction', methods=['GET'])
def get_prediction():
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
    app.run()