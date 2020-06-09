import os
import json
import time
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError

#ddb = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
aws_region = os.getenv('LAMBDA_AWS_REGION', 'us-east-1')
table_name = os.getenv('VISITS_TABLE', 'crc_visits')
ddb = boto3.resource('dynamodb', region_name=aws_region)

# function_response_message = {
#     'code': '',
#     'message': ''
# }

# helper function to json serialize decimal object, 
# cannot access raw json output using high-level boto3.resource method
def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        if float(obj).is_integer():
            return int(obj)
        else:
            return float(obj)
    raise TypeError

def delete_table(name, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name=aws_region)

    table = dynamodb.Table(name)
    table.delete()

def create_visits_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name=aws_region)

    try:
        tableExists = dynamodb.meta.client.describe_table(
            TableName=table_name
            )
        return 'Table Status: {}. Item Count: {}'.format(tableExists['Table']['TableStatus'], tableExists['Table']['ItemCount'])

    except ClientError as e:
        if e.response['Error']['Code'] == "ResourceNotFoundException":
            #print(e.response['Error']['Message'])
            print('Creating table {}.'.format(table_name))
            table = dynamodb.create_table(
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
                },
            )
            #dynamodb.meta.client.get_waiter('table_exists').wait(TableName=table)
            #return table.table_status
        else:
            raise
            #print(e.response['Error']['Code'])

def put_site(site, table_name, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name=aws_region)

    function_response_message = {}

    timestamp = int(time.time())

    table = dynamodb.Table(table_name)
    
    try:
        response = table.put_item(
            Item={
                'site': site,
                'counter': 1,
                'last_updated': timestamp
            },
            # Prevent overwrite to existing data. Use update function.
            ConditionExpression='attribute_not_exists(site)',
            ReturnValues="ALL_OLD"
        )

    except ClientError as e:
        # catch other errors except ConditionalCheckFail
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            function_response_message['code'] = 'Error'
            function_response_message['message'] = 'Item Exists. Use update.'
            return function_response_message
        else:
            raise
    else:
        print('Item Added')
        function_response_message['code'] = 'Success'
        function_response_message['message'] = 'Item Added'
        return function_response_message
        
def get_site(site, table_name, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name=aws_region)
    
    function_response_message = {}

    table = dynamodb.Table(table_name)
    try:
        response = table.get_item(Key={'site': site})
    
    except ClientError as e:
        return 'Error: {}. {}'.format(e.response['Error']['Code'], e.response['Error']['Message'])
        # if e.response['Error']['Code'] == "ResourceNotFoundException":
        #     #raise
        #     return 'Error: {}. {}'.format(e.response['Error']['Code'], e.response['Error']['Message'])
    else:
        if 'Item' not in response:
            print('Item not found.')
            function_response_message['code'] = 'Error'
            function_response_message['message'] = 'Item not found'
            return function_response_message
            #return put_site(site)
        else:
            function_response_message['code'] = 'Success'
            function_response_message['data'] = response['Item']
            return function_response_message
            #return response['Item']

def update_site(site, table_name, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name=aws_region)
    
    function_response_message = {}

    timestamp = int(time.time())
    table = dynamodb.Table(table_name)
    try:
        response = table.update_item(
            Key={
                'site': site
            },
            ConditionExpression='attribute_exists(site)',
            UpdateExpression='set last_updated = :t, #c = #c + :inc',
            ExpressionAttributeNames={
                # Since counter is a reserved keyword
                '#c': 'counter'
            },
            ExpressionAttributeValues={
                ':t': timestamp,
                ':inc': 1
            },
            ReturnValues="UPDATED_NEW"
        )

    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print('Item not found')
            function_response_message['code'] = 'Error'
            function_response_message['message'] = 'Item not found'
            return function_response_message
            #return put_site(site)
        else:
            raise
    else:
        function_response_message['code'] = 'Success'
        function_response_message['data'] = response['Attributes']
        return function_response_message
        #return response['Attributes']

def lambda_handler(event, context):
    #delete_table(table_name,ddb)
    #visits = create_visits_table(ddb)
    #print(visits)
    
    # prepare response
    response = {
        'statusCode': 0,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        'body': ''
    }
    
    operation = event['httpMethod']
    
    if operation == 'GET':
        data = event['pathParameters']
        site = get_site(data['website'], table_name, ddb)
        print(site)
        
        response['statusCode'] = 200
        response['body'] = json.dumps(site, default=decimal_default_proc)
        
        return response
        
    elif operation == 'POST':
        data = json.loads(event['body'])
        print(data)
        
        # handling incorrect body
        if 'website' not in data:
            response['statusCode'] = 400
            response['body'] = '{ "code": "Error", "message": "Incorrect body" }'
            return response
            
        else:
            site = update_site(data['website'], table_name, ddb)

            # if it is a new site
            if 'Error' in site['code']:
                put_site(data['website'], table_name, ddb)
                site = get_site(data['website'], table_name, ddb)
                
                response['statusCode'] = 200
                response['body'] = json.dumps(site, default=decimal_default_proc)
                return response
            
            else:
                response['statusCode'] = 200
                response['body'] = json.dumps(site, default=decimal_default_proc)
        
                return response
        
    else:
        response['statusCode'] = 400
        response['body'] = '{ "code": "Error", "message": "Unsupported operation" }'
        return response

    #return {
    #    'statusCode': 200,
    #    'body': json.dumps('hello from lambda')
    #}

