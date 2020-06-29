import json
import boto3
import unittest
import handler
from moto import mock_apigateway

class TestHelloHandler(unittest.TestCase):
    def test_hello_handler(self):
        expect_body = json.dumps({'message':'Go Serverless v1.0! Your function executed successfully!', 'input': None})
        expect = {'statusCode': 200, 'body': expect_body }
        res = handler.hello(None, None)
        print(res)
        self.assertDictEqual(expect, res)
        