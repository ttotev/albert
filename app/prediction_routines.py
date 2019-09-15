import random

def predict(model, prediction_request):
    """ Mock function
    In place of the actual routines required
	for inference the category(ies) of a given text.
    
    Structure of 'model':
    DynamoDB record content for the reference model

    Structure of 'prediction_request':
    'model_id' -- model ID reference
    'text' -- text for classification
    'n_top' -- only top N labels

    TODO:
    Implement SpaCy inference routines based on reference
        model and supplied text
    """
    # Simulate prediction of labels assignment using random weights
    options = ["CHARGES", "SAVING", "DEBT", "INSURANCE"
        , "ACCOUNT_LINKING", "BILLS", "SPENDING", "BUDGET"]
    ranoptions = [(o, random.random()) for o in options]
    ordoptions = sorted(ranoptions, key=lambda x: x[1], reverse=True)
    return ordoptions[:prediction_request['n_top']]

if __name__ == "__main__":
    p = predict()
    print(p)