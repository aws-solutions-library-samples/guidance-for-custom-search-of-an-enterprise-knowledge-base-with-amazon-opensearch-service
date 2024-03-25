import json
import boto3
import os
from uuid import uuid4
import time

BUCKET = os.environ.get('BUCKET')
HOST = os.environ.get('HOST')
REGION = os.environ.get('REGION')
SEARCH_ENGINE = os.environ.get('SEARCH_ENGINE')
TABLE_NAME = os.getenv('TABLE_NAME')
PRIMARY_KEY = os.getenv('PRIMARY_KEY')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def validate_env_vars():
    required_env_vars = ['BUCKET', 'HOST', 'REGION', 'SEARCH_ENGINE', 'TABLE_NAME', 'PRIMARY_KEY']
    missing_env_vars = [var for var in required_env_vars if not os.environ.get(var)]

    if missing_env_vars:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Missing required environment variables: {", ".join(missing_env_vars)}'}),
            'headers': {'Access-Control-Allow-Origin': '*'}
        }

    return None

def validate_input(item):
    required_params = ['id', 'index', 'language', 'sourceKey', 'chunkSize', 'embeddingEndpoint']
    missing_params = [param for param in required_params if param not in item or not item[param]]

    if missing_params:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Missing required parameters: {", ".join(missing_params)}'}),
            'headers': {'Access-Control-Allow-Origin': '*'}
        }

    return None

def update_item(key, update_expression, expression_values, expression_keys):
    # Create a DynamoDB resource
    dynamodb = boto3.resource('dynamodb')

    # Get the table
    table = dynamodb.Table(TABLE_NAME)

    # Update the item
    response = table.update_item(
        Key=key,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expression_keys
    )

    return response

def lambda_handler(event, context):
    # Validate environment variables
    env_var_error = validate_env_vars()
    if env_var_error:
        return env_var_error

    glue = boto3.client('glue')

    if 'body' not in event:
        return {'statusCode': 400, 'body': 'invalid request, you are missing the parameter body'}

    item = event['body'] if isinstance(event['body'], dict) else json.loads(event['body'])
    item["jobInfo"]["createdAt"] = int(time.time())
    item = item["jobInfo"]

    # Validate input parameters
    validation_error = validate_input(item)
    if validation_error:
        return validation_error

    # Add a create time in to item["jobInfo"] use current timestamp
    print(f"item:{item}")
    if not item.get(PRIMARY_KEY):
        item[PRIMARY_KEY] = str(uuid4())
    print(f"item:{item}")
    table.put_item(Item=item)

    itemId = item.get('id')
    index = item.get('index')
    language = item.get('language')
    object_key = item.get('sourceKey')
    chunk_size = str(item.get('chunkSize'))
    embedding_endpoint_name = item.get('embeddingEndpoint', "")

    print("--id:", itemId)
    print("--index:", index)
    print("--language:", language)
    print("--sourceKey:", object_key)
    print("--chunkSize:", chunk_size)
    print("--embeddingEndpoint:", embedding_endpoint_name)
    print("--BUCKET:", BUCKET)
    print("--HOST:", HOST)
    print("--REGION:", REGION)
    print("--SEARCH_ENGINE:", SEARCH_ENGINE)
    print("--TABLE_NAME:", TABLE_NAME)
    print("--PRIMARY_KEY:", PRIMARY_KEY)

    glue.start_job_run(JobName="my-glue-job",
                       Arguments={
                           "--id": itemId,
                           "--index": index,
                           "--language": language,
                           "--sourceKey": object_key,
                           "--chunkSize": chunk_size,
                           "--embeddingEndpoint": embedding_endpoint_name,
                           "--BUCKET": BUCKET,
                           "--HOST": HOST,
                           "--REGION": REGION,
                           "--SEARCH_ENGINE": SEARCH_ENGINE,
                           "--TABLE_NAME": TABLE_NAME,
                           "--PRIMARY_KEY": PRIMARY_KEY
                       }
                       )

    return {
        'statusCode': 200,
        'body': json.dumps('Successful'),
        "headers": {
            "Access-Control-Allow-Origin": '*'
        }
    }
