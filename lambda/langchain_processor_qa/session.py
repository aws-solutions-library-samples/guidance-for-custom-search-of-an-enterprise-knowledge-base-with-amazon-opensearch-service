import boto3
import json

def get_session_info(table_name, session_id):

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    session_result = ""
    response = table.get_item(Key={'session-id': session_id})
    if "Item" in response.keys():
        session_result = json.loads(response["Item"]["content"])
    else:
        session_result = ""

    return session_result
    
    
def update_session_info(table_name, session_id, question, answer, intention):

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    session_result = ""

    response = table.get_item(Key={'session-id': session_id})

    if "Item" in response.keys():
        chat_history = json.loads(response["Item"]["content"])
    else:
        chat_history = []

    chat_history.append([question, answer, intention])
    content = json.dumps(chat_history)

    response = table.put_item(
        Item={
            'session-id': session_id,
            'content': content
        }
    )

    if "ResponseMetadata" in response.keys():
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            update_result = "success"
        else:
            update_result = "failed"
    else:
        update_result = "failed"

    return update_result