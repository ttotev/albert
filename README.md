# Data Engineer Case Study at Albert

## Concepts

The solution is based on RESTful services built in Flask/Python/Celery - [text_cat_server.py](./app/text_cat_server.py)

SpaCy routines for NLP text classification are not implemented but provisioned.
Mock functions - [training_routines.py](./app/training_routines.py) and [prediction_routines.py](./app/prediction_routines.py) are in place to simulate training and inference tasks.

Datasets for training are stored in AWS S3 in JSON format.
Trained spaCy text classification models are stored in AWS S3 under separate prefexes.

## Provided API endpoints

* /models - GET - retrieve all classification models
* /models - POST - train a new model or update an existing one
* /models/<model_id> - DELETE - remove a model and all related objects
* /prediction - GET - classify a text based on trained model

*Details about the input parameters are given in the comments of the related functions*

## Infrastructure Components

Two deployment options are provided - **local** and **AWS**.

Both require the following setup:

* AWS account for enabling required services
* AWS DynamoDB Table to store references and links to trained models, S3 buckets names, training sets names, hyperparameters

### Running the sample application locally on Ubuntu 18.04 box with access to Internet

Execute the following commands:
```
# the usual system update routines and required packages installation
sudo apt update
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y
sudo apt install awscli -y
sudo apt install python3-pip -y
sudo apt install redis-server -y
sudo systemctl restart redis.service
sudo apt install python3-venv -y

# AWSCLI has to be installed and configured to access a AWS account with admin rights
aws configure

# pull the latest version of the app
git clone https://github.com/ttotev/albert.git

# use python virtual environment to install the necessary python modules
cd albert
python3 -m venv .env
source .env/bin/activate
sudo .env/bin/pip install -r requirements.txt

# run celery in background to prevent API blocking due to long running routines
cd app
nohup ../.env/bin/celery worker -A text_cat_server.celery --loglevel=info &

# run the app
python text_cat_server.py
```
After the server is running successfully, proceed to testing the app.

### Running the sample application in AWS

Building the underlying infrastructure and application components are handled with AWS CloudFormation template.

1. Create a ['Key Pair'](https://console.aws.amazon.com/ec2/home?region=us-east-1#KeyPairs:sort=keyName)
2. Access [CloudFormation console page](https://console.aws.amazon.com/cloudformation) and click 'Create stack'.
3. Select 'Upload a template file'
4. Click on 'Choose file' and pick [aws_cloudformation_template.yaml](aws_cloudformation_template.yaml).
5. Click Next
6. Enter a 'Stack name'. For example, 'AlbertCase'.
7. In Parameters, for 'KeyName', pick the created earlier 'Key Pair'.
8. Leave 'SSHLocation' as it, or enter your IP address to restrict the access only to you.
9. Click Next
10. Leave the default in 'Configure stack options' page.
11. Click Next
12. Review the parameters and check on the Capabilities: Checkmark for 'I acknowledge that AWS CloudFormation might create IAM resources with custom names.'
13. Click button 'Create stack'.
14. Keep an eye on the 'Outputs' tab and refresh regularly.
15. When the resources are ready the PublicIP is displayed.
16. It may take another 5 mins for Ubuntu to update/upgrade system packages and deploy the python app.

The following services are enabled and integrated in AWS:

* EC2 Instance
* Security Group
* IAM Role
* DynamoDB Table

After the server is running successfully, proceed to testing the app.

## Run the application with sample data

To access the application running locally use *localhost*. For AWS deployment use the *IP address* provided in the 'Outputs' section of the CloudFormation stack.

Assuming the API server is running on http://*[address]*:5000, here are some API calls:

```
# POST - Train a model
curl -i -H "Content-Type: application/json" -X POST -d '{"id":"tc-01", "s3bucket":"albert-textcats", "training_object":"trainingSet.json"}' http://[address]:5000/models
```
```
# POST - Force update/retrain an existing model
curl -i -H "Content-Type: application/json" -X POST -d '{"force_update":"True", "id":"tc-01", "s3bucket":"albert-textcats-best", "training_object":"trainingSet.json"}' http://[address]:5000/models
```
```
# DELETE a model
curl -i -H "Content-Type: application/json" -X DELETE http://[address]:5000/models/tc-02
```
```
# GET a list of all models
curl -i -H "Content-Type: application/json" -X GET http://[address]:5000/models
```
```
# GET a prediction
curl -i -H "Content-Type: application/json" -X GET -d '{"model_id":"tc-01", "text":"I want to save for vacation!"}' http://[address]:5000/prediction
```
```
# GET the top one prediction
curl -i -H "Content-Type: application/json" -X GET -d '{"n_top": "1", "model_id":"tc-01", "text":"I want to save for vacation!"}' http://[address]:5000/prediction
```

## Tests

Basic unit tests are included in [tests.py](./app/tests.py)

## Ideas for improvements

* Separate application components into Docker Images
* Use AWS ECS or EKS to run the containers
* Run ECS on Spot Instances to reduce expenses
* Implement monitoring and healthy checks
* Put the execution routines behind AWS API Gateway for setting up a single entry point, security, authentication, authorization and caching
* Use AWS Lambda for text classification prediction
* Research options to retrain the models with data immediately after it has been labeled/classified, instead of batch precessing later
* Version control the trained models