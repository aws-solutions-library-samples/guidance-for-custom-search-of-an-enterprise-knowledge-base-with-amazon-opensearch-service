import boto3
import json
import requests
import time
from collections import defaultdict
from requests_aws4auth import AWS4Auth
import os


host = os.environ.get('host')  
num_output = 50

ENDPOINT_NAME = 'huggingface-inference-text2vec-base-chinese-v1'
headers = { "Content-Type": "application/json" }
runtime= boto3.client('runtime.sagemaker')
# retrieve secret manager value by key using boto3                                             
sm_client = boto3.client('secretsmanager')
master_user = sm_client.get_secret_value(SecretId='opensearch-master-user')['SecretString']
data= json.loads(master_user)
username = data.get('username')
password = data.get('password')
awsauth = (username, password)
num_output = 50

def get_vector(q):
  payload = json.dumps({"inputs":[q]})
  response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                     ContentType="application/json",
                                     Body=payload)
  result = json.loads(response['Body'].read().decode())[0][0][0]
  return result

  
def search_using_knn(q, index, source_includes, size, k):
    print(1, q)
    query = {
          "size": num_output,
          "_source": {
            "includes": source_includes
          },
          "size": size,
          "query": {
            "knn": {
              "question_vector": {
                "vector": get_vector(q),
                "k": k
              }
            }
          }
        }
    r = requests.post(host + index + '/_search', auth=awsauth, headers=headers, json=query)
    print(r.text)
    return r.text

def split_sentences(q):
    def is_letter_or_number(s):
        if "0" <= s <= "9" or "a" <= s <= "z" or "A" <= s <= "Z":
            return True
        return False
    
    slices = []
    i = 0
    while i < len(q):
        if is_letter_or_number(q[i]):
            tmp = [q[i]]
            i += 1
            while i < len(q) and is_letter_or_number(q[i]):
                tmp .append(q[i])
                i += 1
            slices.append('*'+'*'.join(tmp)+'*')
            slices.append(''.join(tmp))
        else:
            tmp = q[i]
            i += 1
            while i < len(q) and is_letter_or_number(q[i])==False:
                tmp += q[i]
                i += 1
            slices.append(tmp)
    return ' '.join(slices)

# Lambda execution starts here
def lambda_handler(event, context):
    index = event['queryStringParameters']['ind']
    print('index', index)
    source_includes = ["question", "answer"]
    fields = ["question"]
    if event['queryStringParameters']['knn'] == "1":
      print (event['queryStringParameters']['q'])
      r = search_using_knn(event['queryStringParameters']['q'], event['queryStringParameters']['ind'], 
                          source_includes, num_output, 10)
    else:
      q = event['queryStringParameters']['q']
      q = split_sentences(q)
      if 'ml' not in event['queryStringParameters']:
        query = {
          "size": num_output,
            "_source": {
                "includes": source_includes
              },
          'query': {
            "multi_match": {
              "query": event['queryStringParameters']['q'],
              "fields": fields
            }
          }
        }
      else:
        query = {
          "size": num_output,
            "_source": {
                "includes": source_includes
              },
          "query": {
            "multi_match": {
              "query": event['queryStringParameters']['q'],
              "fields": fields
            }
          },
          "rescore": {
            "query": {
              "rescore_query": {
                "sltr": {
                  "params": {
                    "keywords": event['queryStringParameters']['q']
                  },
                  "model": event['queryStringParameters']['ml']
                }
              }
            }
          }
        }
      r = requests.post(host + index + '/_search', auth=awsauth, headers=headers, json=query)
      r = r.text
    
    # print(r)
    # # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }
    response['body'] = json.dumps({'body': json.loads(r), 
                    'datetime':time.time()})
    return response
