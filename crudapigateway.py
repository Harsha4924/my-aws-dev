import json
from aiohttp import ClientError
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
dynamodb_table = dynamodb.Table('mycrudtable2')


def lambda_handler(event, context):
    print('request_event', event)
    single_employee_path = '/employee'
    multi_employee_path = '/employees'
    status_path = '/status'
    response = None
    try:
        http_method = event.get('httpMethod')
        get_path = event.get('path')
        if http_method == 'GET' and get_path == status_path:
            response = build_response(200, 'Service is operational')
        elif http_method == 'GET' and get_path == multi_employee_path:
            response = get_all_employees()
        elif http_method == 'GET' and get_path == single_employee_path:
            # response = get_single_employee()
            employee_id = event['queryStringParameters']['employeeid']
            response = get_single_employee(employee_id)
        elif http_method == 'POST' and get_path == single_employee_path:
            get_body = json.loads(event['body'])
            print("body", get_body)
            print("path", get_path)
            response = save_employee(get_body)
        elif http_method == 'PATCH' and get_path == single_employee_path:
            body = json.loads(event['body'])
            response = update_employee(body['employee_id'], body['update_key'], body['update_value'])
        elif http_method == 'DELETE' and get_path == single_employee_path:
            pass




    except Exception as e:
        return e
    return response

def get_all_employees():
    try:
        scan_params = {
            'TableName': dynamodb_table.name
        }
        return build_response(200, scan_dynamo_records(scan_params, []))
    except Exception as e:
        return e

def scan_dynamo_records(scan_params, my_list):
    response = dynamodb_table.scan(**scan_params)
    my_list.extend(response.get('Items', []))
   
    if 'LastEvaluatedKey' in response:
        scan_params['ExclusiveStartKey'] = response['LastEvaluatedKey']
        return scan_dynamo_records(scan_params, my_list)
    else:
        return {'employees': my_list}

def get_single_employee(employee_id):
    try:
        response = dynamodb_table.get_item(Key={'employee_id': employee_id})
        return build_response(200, response.get('Item'))
    except Exception as e:
        print('Error:', e)
        return build_response(400, e.response['Error']['Message'])

def save_employee(get_body):
    try:
        dynamodb_table.put_item(Item=get_body)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': get_body
        }
        return build_response(200, body)
    except Exception as e:
        print('Error:', e)
        return build_response(400, e.response['Error']['Message'])

def update_employee(employee_id, update_key, update_value):
    try:
        response = dynamodb_table.update_item(
            Key={'employee_id': employee_id},
            UpdateExpression=f'SET {update_key} = :value',
            ExpressionAttributeValues={':value': update_value},
            ReturnValues='UPDATED_NEW'
        )
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }
        return build_response(200, body)
    except ClientError as e:
        print('Error:', e)
        return build_response(400, e.response['Error']['Message'])


def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body)
    }

