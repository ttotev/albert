# Data Engineer Case Study at Albert

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install redis-server
sudo service redis-server restart

../.env/bin/celery worker -A text_cat_server.celery --loglevel=info

## Concepts

The solution is based on RESTful services built in Flask/Python. 
SpaCy routines are not implemented. Instead mock functions are in place to simulate training and inference tasks.
Datasets for training are stored in AWS S3 in JSON format.
Trained spaCy text classification modules are stored in AWS S3 under separate prefexes.

## Infrastructure Components

* AWS account is required for enabling required services
* AWSCLI has to be installed and configured to access AWS account if running in development or text mode
* EC2 Instance - runtime environment
* AWS DynamoDB Table - stores references and links to trained models, S3 buckets names, training sets names, hyperparameters

## Tests

Basic tests are included in tests.py

## Examples:

Assuming the API server is running on http://localhost:5000

```
# POST / Train a model
curl -i -H "Content-Type: application/json" -X POST -d '{"id":"tc-01", "s3bucket":"albert-textcats", "training_object":"trainingSet.json"}' http://localhost:5000/models
```
```
# POST force_update/retrain a model
curl -i -H "Content-Type: application/json" -X POST -d '{"force_update":"True", "id":"tc-01", "s3bucket":"albert-textcats-best", "training_object":"trainingSet.json"}' http://localhost:5000/models
```
```
# DELETE a model
curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/models/tc-02
```
```
# GET a list of all models
curl -i -H "Content-Type: application/json" -X GET http://localhost:5000/models
```
```
# GET prediction
curl -i -H "Content-Type: application/json" -X GET -d '{"model_id":"tc-01", "text":"I want to save for vacation!"}' http://localhost:5000/prediction
```
```
# GET the top one prediction
curl -i -H "Content-Type: application/json" -X GET -d '{"n_top": "1", "model_id":"tc-01", "text":"I want to save for vacation!"}' http://localhost:5000/prediction
```