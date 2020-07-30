import json
import os
import logging
from datetime import datetime
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError
from lambda_decorators import cors_headers

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)

def decimal_encode(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError

IS_OFFLINE = os.environ.get('IS_OFFLINE')
IS_LOCAL = os.environ.get('IS_LOCAL')

aws_region = os.environ.get('LAMBDA_AWS_REGION', 'us-east-1')
table_name = os.environ.get('VISITS_TABLE', 'crc_visits')

if((IS_LOCAL) or (IS_OFFLINE)):
    ddb = boto3.resource('dynamodb',
                    endpoint_url='http://localhost:8000',
                    region_name='localhost',
                    aws_access_key_id='foo',
                    aws_secret_access_key='bar')
    ddb_table = ddb.Table(table_name)
    _logger.debug('DDB Connect: {}'.format(ddb_table))

else:
    ddb = boto3.resource('dynamodb', region_name=aws_region)
    ddb_table = ddb.Table(table_name)
    _logger.debug('DDB Connect: {}'.format(ddb_table))

def put_item(data):
    item = {}
    item['site'] = data
    item['counter'] = 0
    item['last_updated'] = int(datetime.utcnow().timestamp())

    res = ddb_table.put_item(
        Item = item
    )

    _logger.info('DDB Put response: {}'.format(res))
    return item

def get_items():
    try:
        res = ddb_table.scan()
        data = res['Items']
        
        while 'LastEvaluatedKey' in res:
            res = ddb_table.scan(ExclusiveStartKey=res['LastEvaluatedKey'])
            data.extend(res['Items'])

        _logger.info('DDB Get response: {}'.format(data))
        if not bool(data):
            return { 'error': { 'message': 'items not found' } }
        else:
            return data
    except ClientError as err:
        return err.response['Error']

def get_item(data):
    try:
        res = ddb_table.get_item(
            Key={
                'site': data
            }
        )
        data = res.get('Item', {})
        _logger.info('DDB Get response: {}'.format(data))
        if not bool(data):
            return { 'error': { 'message': 'item not found' } }
        else:
            return data

    except ClientError as err:
        return err.response['Error']

def update_item(data):

    site = data
    time_now = int(datetime.utcnow().timestamp())

    try:
        res = ddb_table.update_item(
            Key={
                'site': site
            },
            UpdateExpression='ADD #c :c SET last_updated = :t',
            ExpressionAttributeNames={
                    # Since counter is a reserved keyword
                    '#c': 'counter'
            },
            ExpressionAttributeValues={
                ':t': time_now,
                ':c': 1
            },
            ReturnValues="ALL_NEW"
        )

        _logger.info('DDB Put response: {}'.format(res))
        return res['Attributes']

    except ClientError as err:
        return err.response['Error']

@cors_headers
def hello(event, context):
    _logger.info('Event: {}'.format(json.dumps(event)))
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        # "date": int(datetime.utcnow().timestamp()),
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    _logger.info('Response: {}'.format(json.dumps(response)))
    return response

@cors_headers
def add_site(event, context):
    _logger.info('Event: {}'.format(json.dumps(event)))
    data = json.loads(event['body'])
    site = data['website']

    body = put_item(site)

    response = {
        "statusCode": 200,
        "body": json.dumps(body, default=decimal_encode)
    }

    _logger.info('Response: {}'.format(json.dumps(response)))
    return response

@cors_headers
def get_sites(event, context):
    _logger.info('Event: {}'.format(json.dumps(event)))

    body = get_items()

    response = {
        "statusCode": 200,
        "body": json.dumps(body, default=decimal_encode)
    }

    _logger.info('Response: {}'.format(json.dumps(response)))
    return response

@cors_headers
def get_site(event, context):
    _logger.info('Event: {}'.format(json.dumps(event)))
    site = event['pathParameters']['website']
    body = get_item(site)

    response = {
        "statusCode": 200,
        "body": json.dumps(body, default=decimal_encode)
    }

    _logger.info('Response: {}'.format(json.dumps(response)))
    return response

@cors_headers
def update_site(event, context):
    _logger.info('Event: {}'.format(json.dumps(event)))
    data = json.loads(event['body'])

    if 'website' not in data:
        body = { 'error': { 'message':'incorrect schema' } }
        response = {
            "statusCode": 400,
            "body": json.dumps(body, default=decimal_encode)
        }
    else:
        site = data['website']

        body = update_item(site)

        response = {
            "statusCode": 200,
            "body": json.dumps(body, default=decimal_encode)
        }

    _logger.info('Response: {}'.format(json.dumps(response)))
    return response