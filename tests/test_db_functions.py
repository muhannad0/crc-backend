import json
import os
import unittest
import boto3
from moto import mock_dynamodb2

from .ddb_config import ddb_init

@mock_dynamodb2
class TestDatabaseFunctions(unittest.TestCase):
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

    def test_get_items_non_exist(self):
        """Test if returns error for non existent items"""
        from handler import get_items
        res = get_items()
        # print(res)
        self.assertIn('error', res)

    def test_get_items_exist(self):
        """Test if returns list of items"""
        from handler import get_items, put_item
        data = 'example.com'
        data2 = 'example.org'
        put_item(data)
        put_item(data2)
        res = get_items()
        self.assertTrue(res)
        self.assertGreaterEqual(len(res), 1)

    def test_get_item_non_exist(self):
        """Test if returns error for single non existent item"""
        from handler import get_item
        data = 'example.com'
        res = get_item(data)
        # print(res)
        self.assertIn('error', res)

    def test_get_item_exist(self):
        """Test if returns a single item"""
        from handler import get_item, put_item
        data = 'example.com'
        put_item(data)
        res = get_item(data)
        self.assertTrue(res)
        self.assertEqual(len(res), 3)
        self.assertIn('counter', res)
        self.assertIn('last_updated', res)
        self.assertIn(data, res['site'])

    def test_update_item_not_exist(self):
        """Test if can add non existing item"""
        from handler import update_item
        data = 'example.com'
        res = update_item(data)
        # print(res)
        self.assertTrue(res)
        self.assertIn('counter', res)
        self.assertIn('last_updated', res)
        self.assertIn(data, res['site'])
        self.assertEqual(1, res['counter'])
        self.assertNotEqual(0, res['last_updated'])

    def test_update_item_exist(self):
        """Test if can update counter for existing item"""
        from handler import update_item
        data = 'example.com'
        update_item(data) # update once
        res = update_item(data) # update twice
        # print(res)
        self.assertTrue(res)
        self.assertIn('counter', res)
        self.assertIn('last_updated', res)
        self.assertIn(data, res['site'])
        self.assertEqual(2, res['counter']) # counter should be 2
        self.assertNotEqual(0, res['last_updated'])
