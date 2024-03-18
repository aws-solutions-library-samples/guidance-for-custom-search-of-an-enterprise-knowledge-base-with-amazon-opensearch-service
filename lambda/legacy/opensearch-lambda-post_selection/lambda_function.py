import json
import boto3


def lambda_handler(event, context):
    if event['Method'] == 'insert_feedback':
        try:
            lambda_inv = boto3.client("lambda")
            payload = event
            res = lambda_inv.invoke(FunctionName='opensearch-lambda-insert_feedback', 
                                InvocationType='Event', Payload=json.dumps(payload))
            response = {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                "isBase64Encoded": False
            }
            response['body'] = 'insert_feedback succeed'
            return response
            
        except:
            return {
                    'statusCode': 400,
                    'body': 'insert_feedback failed',
                    "headers": {
                        "Access-Control-Allow-Origin": '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    },
                }
    elif event['Method'] == 'create_ltr_model':
        lambda_inv = boto3.client("lambda")
        payload = event
        payload['opensearch']['feature_set'] = json.dumps(payload['opensearch']['feature_set'].replace(' ','').split('\n'))
        payload['dynamodb']['before_day'] = int(payload['dynamodb']['before_day'])
        res = lambda_inv.invoke(FunctionName='open-search_xgb_train_deploy', 
                            InvocationType='Event', Payload=json.dumps(payload))
        return {
                    'statusCode': 200,
                    # 'body': str(res),
                    'body': payload,
                    "headers": {
                        "Access-Control-Allow-Origin": '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    },
                }
    
