import random
import time

def train(app, train_request):
	""" ASYNC invoked Mock Function
	In place of the actual routines required
	for training the text categorization model.
	Training a model may take significant time.

	Structure of 'train_request':
    'id' -- model ID/name
    's3bucket' -- AWS S3 bucket name containing the training file
    'training_object' -- JSON file with training texts and labels
    'spacy_model' -- base SpaCy model name
    'n_texts' -- maximum text used for training
    'n_iter' -- number of training iteractions

	TODO:
	1. Implement SpaCy training routine
	2. Maintenance of training files on S3
	3. Saving the trained model to S3 bucket
	"""
	# Simulate long running function
	sec = random.randrange(30, 90)
	print("Slow running training function")
	if app.testing != True:
		print(f'Sleeping {sec} secs')
		time.sleep(sec)
	else:
		print('Test mode - fast run')

if __name__ == "__main__":
    train({})
