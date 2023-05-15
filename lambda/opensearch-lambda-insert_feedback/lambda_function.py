import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb')
        table_name = event['table_name']
        search_inputs = json.dumps({"datetime": event['datetime'], "Inputs": event['search_inputs']}, ensure_ascii=False)
        _id = event['_id']
        feedback = event['feedback']
        
        table = dynamodb.Table(table_name)
        with table.batch_writer() as batch:
            batch.put_item(Item={"SearchInputs": search_inputs, "_id": _id, "Feedback": feedback})
            
        return {
            'statusCode': 200,
            'body': 'insert successfully'
        }

    except:
        return {
            'statusCode': 400,
            'body': 'inserting failed'
        }
