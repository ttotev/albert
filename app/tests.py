import unittest
from text_cat_server import app

class TestTextCatServer(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_model_post_empty(self):
        rv = self.app.post('/models')
        self.assertIn(b'Required parameters not supplied', rv.data)

    def test_model_post_update_with_force(self):
        rv = self.app.post('/models'
                , json={"id":"tc-01"
                    , "force_update":"True"
                    , "s3bucket":"albert-textcats"
                    , "training_object":"trainingSet.json"}
            )
        json_data = rv.get_json()
        self.assertIn('Attributes', json_data)

    def test_model_post_update_no_force(self):
        rv = self.app.post('/models'
                , json={"id":"tc-01"
                    , "s3bucket":"albert-textcats"
                    , "training_object":"trainingSet.json"}
            )
        self.assertIn(b'Cannot update existing model. Use force_update:True', rv.data)

    def test_model_get_all(self):
        rv = self.app.get('/models')
        self.assertEqual(rv.status, '200 OK')

    def test_model_get_data(self):
        rv = self.app.get('/models')
        self.assertIn(b'data', rv.data)

if __name__ == '__main__':
    unittest.main()