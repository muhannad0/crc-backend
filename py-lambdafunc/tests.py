import boto3
from botocore.exceptions import ClientError
import visits
import unittest

# assertion comparison format: expected result vs. actual result
class TestHttpOperation(unittest.TestCase):
    def test_cors_headers(self):
        """
        Testing for CORS support in the response headers
        """
        event = { 'httpMethod': 'PUT' }
        null = None
        result = visits.lambda_handler(event, null)
        self.assertEqual({'Access-Control-Allow-Origin': '*'}, result['headers'])

    def test_unsupported_operation(self):
        """
        Testing for handling unsupported http methods
        """
        event = { 'httpMethod': 'PUT' }
        null = None
        result = visits.lambda_handler(event, null)
        self.assertIn('Error', result['body'])

    def test_incorrect_body(self):
        """
        Testing for incorrect body submitted during POST
        """
        event = { 'body': '{\"webs\": \"example.net\"}', 'httpMethod': 'POST' }
        null = None
        result = visits.lambda_handler(event, null)
        self.assertIn('Error', result['body'])

class TestDynamoDbOperation(unittest.TestCase):
    ddb = None
    db_endpoint = "http://localhost:8000" # testing against local dynamodb
    db_regions = "us-east-1" # testing against local dynamodb
    table_name = "crc_visits_test"

    # Class method so that it runs only once (unlike setUp does for each test)
    @classmethod
    def setUpClass(cls):
        # Setup database
        cls.ddb = boto3.resource('dynamodb', endpoint_url=cls.db_endpoint, region_name=aws_region)
        
        # Create test table
        try:
            table = cls.ddb.create_table(
                TableName=cls.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'site',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'site',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            )
            
            table.meta.client.get_waiter('table_exists').wait(TableName=cls.table_name)
            print(table.table_status)

        except ClientError as e:
            raise
            
        # Insert some sample data
        table = cls.ddb.Table(cls.table_name)
        try:
            table.put_item(
                Item={
                    'site': 'example.com',
                    'counter': 1,
                    'last_updated': ''
                }
            )
        except ClientError as e:
            raise

    @classmethod
    def tearDownClass(cls):
        table = cls.ddb.Table(cls.table_name)
        table.delete()
        cls.ddb = None

    def test_put_item_new(self):
        website = "example.net"
        result = visits.put_site(website, self.table_name, self.ddb)
        self.assertIn('Success', result['code'])
    
    def test_put_item_exists(self):
        website = "example.com"
        result = visits.put_site(website, self.table_name, self.ddb)
        self.assertIn('Error', result['code'])

    def test_get_item_exits(self):
        website = "example.com"
        result = visits.get_site(website, self.table_name, self.ddb)
        self.assertIn('Success', result['code'])
    
    def test_get_item_not_exits(self):
        website = "example.org"
        result = visits.get_site(website, self.table_name, self.ddb)
        self.assertIn('Error', result['code'])

    def test_update_item_exists(self):
        website = "example.com"
        result = visits.update_site(website, self.table_name, self.ddb)
        self.assertIn('Success', result['code'])
        self.assertIn('last_updated', result['data'])

    def test_update_item_not_exists(self):
        website = "example.org"
        result = visits.update_site(website, self.table_name, self.ddb)
        self.assertIn('Error', result['code'])

    # TODO: Figure out how to pass db object to lambda_handler fn??
    # def test_correct_http_submit_exists(self):
    #     """
    #     Testing for incorrect body submitted during POST
    #     """
    #     event = { 'body': '{\"website\": \"example.com\"}', 'httpMethod': 'POST' }
    #     null = None
    #     result = visits.lambda_handler(event, null)
    #     self.assertIn('Error', result['body'])

# if __name__ == '__main__':
#     unittest.main()