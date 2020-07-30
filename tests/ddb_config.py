import os
import boto3
from moto import mock_dynamodb2

def ddb_init():
    ddb = boto3.resource('dynamodb', region_name='us-east-1')
    table_name = os.getenv('VISITS_TABLE', 'crc_visits')

    ddb_table = ddb.create_table(
        TableName=table_name,
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
            })

    # Wait until the table exists.
    ddb_table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    assert ddb_table.table_status == 'ACTIVE'

    return ddb, ddb_table