# Data Engineer Case Study at Albert

## Concepts

The solution is based on RESTful services built in Flask/Python/Celery - [text_cat_server.py](./app/text_cat_server.py)

SpaCy routines for NLP text classification are not implemented but provision.
Mock functions - [training_routines.py](./app/training_routines.py) and [prediction_routines.py](./app/prediction_routines.py) are in place to simulate training and inference tasks.

Datasets for training are stored in AWS S3 in JSON format.
Trained spaCy text classification models are stored in AWS S3 under separate prefexes.

## Infrastructure Components

Two deployment options are provided - locally and AWS.

Both require the following setup:

* AWS account for enabling required services
* AWS DynamoDB Table - stores references and links to trained models, S3 buckets names, training sets names, hyperparameters

### Running the sample application locally

* Local Linux box with access to Internet
* AWSCLI has to be installed and configured (`aws configure`) to access AWS account

### Running the sample application in AWS

'Key Pair' is required to be created. 
Building the underlying infrastructure and application components are handled with AWS Cloudformation template - [aws_cloudformation_template.yaml](aws_cloudformation_template.yaml).

Create Stack

Upload a template file
Choose file
Next

Stack name: 
Parameters:
KeyName:
SSHLocation:

Configure stack options
Next

Review
Capabilities: Checkmark the 'I acknowledge that AWS CloudFormation might create IAM resources with custom names.'

Click button 'Create stack'.

The deployment and configuration will take about 

https://console.aws.amazon.com/ec2/home?region=us-east-1#KeyPairs:sort=keyName

* EC2 Instance - runtime environment with the required Security Group and IAM Role

## Generic installation steps for Ubuntu 18.04
```
sudo apt update
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y
sudo apt install awscli -y
aws configure
sudo apt install python3-pip -y
sudo apt install redis-server -y
# In /etc/redis/redis.conf set - supervised systemd
sudo systemctl restart redis.service
sudo apt install python3-venv -y
git clone https://github.com/ttotev/albert.git
cd albert
python3 -m venv .env
source .env/bin/activate
sudo .env/bin/pip install -r requirements.txt
cd app
../.env/bin/celery worker -A text_cat_server.celery --loglevel=info
# In different terminal:
cd app
python text_cat_server.py
```
## Provided API endpoints

* /models - GET - retrieve all clasification models
* /models - POST - train a new model or update an existing one
* /models/<model_id> - DELETE - remove a model and all related objects
* /prediction - GET - classify a text based on trained model

Details about the input parameters are given in the comments of the related functions

## Run the application locally with sample data

In a separate terminal:

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

## Tests

Basic tests are included in [tests.py](./app/tests.py)