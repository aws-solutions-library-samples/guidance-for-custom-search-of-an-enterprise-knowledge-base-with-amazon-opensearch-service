import boto3
import json
import requests
import time
from collections import defaultdict
from requests_aws4auth import AWS4Auth
import os

KNN_ENDPOINT_NAME = 'huggingface-inference-eb'
GTM_ENDPOINT_NAME = 'pytorch-inference-llm-v1'
host =  os.environ.get('host') 

# retrieve secret manager value by key using boto3                                             
sm_client = boto3.client('secretsmanager')
master_user = sm_client.get_secret_value(SecretId='opensearch-master-user')['SecretString']
data= json.loads(master_user)
username = data.get('username')
password = data.get('password')
num_output = 10

awsauth = (username, password)


source_includes = ["title","sentence","paragraph","sentence_id","paragraph_id"]
runtime= boto3.client('runtime.sagemaker')
fields = ["sentence"]
headers = { "Content-Type": "application/json" }


def get_results(r):
    res = []
    clean = []
    for i in range(len(r['hits']['hits'])):
        h = r['hits']['hits'][i]
        if h['_source']['paragraph'] not in clean:
          clean.append(h['_source']['paragraph'])
          res.append('<第'+str(i+1)+'条信息>'+h['_source']['paragraph'] + '。</第'+str(i+1)+'条信息>\n')
    return ' '.join(res)

def get_vector(q):
  payload = json.dumps({"inputs":[q]})
  response = runtime.invoke_endpoint(EndpointName=KNN_ENDPOINT_NAME,
                                     ContentType="application/json",
                                     Body=payload)
  result = json.loads(response['Body'].read().decode())[0][0][0]
  # print(result)
  return result
  
def get_answer(question, context):
  def query_endpoint_with_json_payload(encoded_json):
    response = runtime.invoke_endpoint(EndpointName=GTM_ENDPOINT_NAME, ContentType='application/json', Body=encoded_json)
    return response

  def parse_response_texts(query_response):
      model_predictions = json.loads(query_response['Body'].read())
      generated_text = model_predictions["answer"]
      return generated_text
  
  prompt_template = """基于以下已知信息，简洁和专业的来回答用户的问题，并告知是依据哪些信息来进行回答的。
    如果无法从中得到答案，请说 "根据已知信息无法回答该问题" 或 "没有提供足够的相关信息"，不允许在答案中添加编造成分，答案请使用中文。
    
    已知内容:
      """
  prompt_template += context + """
   
    问题:
     """
  prompt_template += question
  payload = {"ask": prompt_template}


  query_response = query_endpoint_with_json_payload(json.dumps(payload).encode('utf-8'))
  generated_texts = parse_response_texts(query_response)
  return generated_texts
  
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
              "sentence_vector": {
                "vector": get_vector(q),
                "k": k
              }
            }
          }
        }
    r = requests.post(host + index + '/_search', auth=awsauth, headers=headers, json=query)
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
    if event['queryStringParameters']['knn'] == "1":
      print (event['queryStringParameters']['q'])
      r = search_using_knn(event['queryStringParameters']['q'], event['queryStringParameters']['ind'], 
                          source_includes, num_output, 10)
    else:
      q = event['queryStringParameters']['q']
      # q = split_sentences(q)
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
      # Make the signed HTTP request
      r = requests.post(host + index + '/_search', auth=awsauth, headers=headers, json=query)
      r = r.text
    
    # print(r)
    content = get_results(json.loads(r))
    print(content[:2000])
    
    suggestion_answer = get_answer(event['queryStringParameters']['q'], content[:2000])
    

    print(suggestion_answer)
    # # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }
    response['body'] = json.dumps(
      {
        'body': json.loads(r), 
        'datetime':time.time(),
        'suggestion_answer': suggestion_answer
      })
    return response
