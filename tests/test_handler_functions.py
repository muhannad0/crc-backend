import json
import os
import unittest
import boto3
from moto import mock_dynamodb2

from ddb_config import ddb_init

@mock_dynamodb2
class TestHandlerFunction(unittest.TestCase):
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

    def setUp(self):
        """Creates the database and table"""
        self.ddb, self.ddb_table = ddb_init()

    def tearDown(self):
        self.ddb_table.delete()
        self.ddb = None

    def test_hello_handler(self):
        from handler import hello
        res = hello(None, None)
        # check if returned a result
        self.assertTrue(res)
        # check if response contains correct properties
        self.assertIn('statusCode', res)
        self.assertIn('headers', res)
        self.assertIn('body', res)
        # check for status code
        self.assertEqual(200, res['statusCode'])
        # check for cors headers
        self.assertIn('Access-Control-Allow-Origin', res['headers'])
 
    def test_get_items_handler(self):
        from handler import add_site, get_sites
        event_data = { 'body': '{\"website\": \"example.com\"}' }
        event_data2 = { 'body': '{\"website\": \"example.net\"}' }
        add_site(event_data, None) # add example.com
        add_site(event_data2, None) # add exampl.net
        res = get_sites(None, None)
        self.assertTrue(res)
        self.assertIn('statusCode', res)
        self.assertIn('headers', res)
        self.assertIn('body', res)
        self.assertEqual(200, res['statusCode'])
        self.assertIn('Access-Control-Allow-Origin', res['headers'])
        self.assertEqual(len(json.loads(res['body'])), 2) # should return 2 items

    def test_get_item_handler(self):
        from handler import add_site, get_site
        event_data = { 'body': '{\"website\": \"example.com\"}' }
        query_event_data = { 'pathParameters': { 'website': 'example.com' } }
        add_site(event_data, None)
        res = get_site(query_event_data, None)
        self.assertTrue(res)
        self.assertIn('statusCode', res)
        self.assertIn('headers', res)
        self.assertIn('body', res)
        self.assertEqual(200, res['statusCode'])
        self.assertIn('Access-Control-Allow-Origin', res['headers'])
        self.assertIn(query_event_data['pathParameters']['website'], json.loads(res['body'])['site']) # should return example.com item

    def test_update_item_handler_incorrect_body(self):
        from handler import update_site
        event_data = { 'body': '{\"web\": \"example.com\"}' }
        res = update_site(event_data, None)
        self.assertTrue(res)
        self.assertIn('statusCode', res)
        self.assertIn('headers', res)
        self.assertIn('body', res)
        self.assertEqual(400, res['statusCode'])
        self.assertIn('Access-Control-Allow-Origin', res['headers'])
        self.assertIn('error', json.loads(res['body'])) # should return error for incorrect schema

    def test_update_item_handler_correct_body(self):
        from handler import update_site
        event_data = { 'body': '{\"website\": \"example.com\"}' }
        res = update_site(event_data, None) # update once
        res = update_site(event_data, None) # update twice
        self.assertTrue(res)
        self.assertIn('statusCode', res)
        self.assertIn('headers', res)
        self.assertIn('body', res)
        self.assertEqual(200, res['statusCode'])
        self.assertIn('Access-Control-Allow-Origin', res['headers'])
        self.assertEqual(json.loads(res['body'])['counter'], 2) # should return 2 for counter value