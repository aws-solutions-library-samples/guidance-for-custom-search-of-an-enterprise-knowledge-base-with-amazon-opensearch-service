import boto3
from boto3.dynamodb.conditions import Key
import time
import json
import requests
from copy import deepcopy
import xgboost as xgb
from collections import defaultdict
import os

base_feat = {
  "query": {
    "bool": {
      "filter": [
        {
          "terms": {
            "_id": []
          }
        },
        {
          "sltr": {
            "_name": "logged_featureset",
            "featureset": "",
            "params": {
              "keywords": ""
            }
          }
        }
      ]
    }
  },
  "ext": {
    "ltr_log": {
      "log_specs": {
        "name": "log_entry",
        "named_query": "logged_featureset"
      }
    }
  }
}

base_feature = {
          "name" : "",
          "params" : [
            "keywords"
          ],
          "template_language" : "mustache",
          "template" : {
            "match" : {}
          }
        }

base_create_feature_set = {
  "featureset" : {
      "name" : "",
      "features" : []
    }
}


def read_db_with_time(datetime, client, table_name):
    Items = []

    response = client.scan(
#             Limit=1,
            ExpressionAttributeValues={
                ':a': {
                    'S': json.dumps({"datetime": datetime}),
                },
            },
            FilterExpression='SearchInputs >= :a',
            TableName=table_name,
        )
    Items = response['Items']

    while 'LastEvaluatedKey' in response:
        response = client.scan(
#             Limit=10,
            ExclusiveStartKey = response['LastEvaluatedKey'],
            ExpressionAttributeValues={
                ':a': {
                    'S': json.dumps({"datetime": datetime}),
                },
            },
            FilterExpression='SearchInputs >= :a',
            TableName=table_name,
        )
        Items.extend(response['Items'])
    return Items

def formulate_item(item):
    _id = item['_id']['S']
    feedback = item['Feedback']['N']
    inputs = json.loads(item['SearchInputs']['S'])['Inputs']
    return inputs, _id, feedback

def formulate_items(items):
    res = defaultdict(dict)
    for item in items:
        inputs, _id, feedback = formulate_item(item)
        if _id not in res[inputs]:
            res[inputs][_id] = int(feedback) * 2 - 1
        else:
            res[inputs][_id] += int(feedback) * 2 - 1
    return res


def check(f_items):
    new_items = {}
    for inputs in f_items:
        ori_rank = [f_items[inputs][key] for key in f_items[inputs]]
        if max(ori_rank) != min(ori_rank):
            new_items[inputs] = f_items[inputs]
    return new_items

def get_ranking(f_items, interval=[0, 4]):
    for inputs in f_items:
        ori_rank = [f_items[inputs][key] for key in f_items[inputs]]
        _min, _max = min(ori_rank), max(ori_rank)
        rank = [int((interval[1]-interval[0])*(i-_min)/(_max-_min)+interval[0]) for i in ori_rank]
        _map = {}
        for i in range(len(rank)):
            _map[ori_rank[i]] = rank[i]
        for key in f_items[inputs]:
            f_items[inputs][key] = _map[f_items[inputs][key]]
    return f_items

def create_feature_set(feature_set_name, feature_names, host, auth, headers):
    r = requests.get(host + '_ltr/_featureset', auth=auth, headers=headers)
    r = json.loads(r.text)
    exist_feature_sets = []
    for ri in r['hits']['hits']:
        exist_feature_sets.append(ri['_source']['name'])
    if feature_set_name in exist_feature_sets:
        return feature_set_name+' was exist'
    
    bcfs = deepcopy(base_create_feature_set)
    bcfs['featureset']['name'] = feature_set_name
    for name in feature_names:
        bf = deepcopy(base_feature)
        bf['name'] = name
        bf['template']['match'] = {name : "{{keywords}}"}
        bcfs['featureset']['features'].append(bf)
    r = requests.post(host + '_ltr/_featureset/' + feature_set_name, auth=auth, headers=headers, json=bcfs)
    return r.text


def get_func_feat(ids, feaatureset, keywords, index_name, host, auth, headers):
    if len(ids) <= 10:
        return get_10_func_feat(ids, feaatureset, keywords, index_name, host, auth, headers)
    else:
        shard = len(ids) // 10 + 1
        feat_val = {}
        for i in range(shard):
            tmp_ids = ids[i*10:(i+1)*10]
            _, tmp_feat_val = get_10_func_feat(tmp_ids, feaatureset, keywords, index_name, host, auth, headers)
            feat_val.update(tmp_feat_val)
        return _, feat_val

def get_10_func_feat(ids, feaatureset, keywords, index_name, host, auth, headers):
    if len(ids) == 0:
        return {}, {}
    base_feat["query"]["bool"]["filter"][0]["terms"]["_id"] = ids
    base_feat["query"]["bool"]["filter"][1]["sltr"]["featureset"] = feaatureset
    base_feat["query"]["bool"]["filter"][1]["sltr"]["params"]["keywords"] = keywords
#     print(json.dumps(base_feat))
    response = requests.post(host + index_name + '/_search', auth=auth, headers=headers, json=base_feat)
    response = json.loads(response.text)
    num_hits = len(response['hits']['hits'])
    feat_val = {}
    for i in range(num_hits):
        hit = response['hits']['hits'][i]
        val = {}
        for log in hit['fields']['_ltrlog'][0]['log_entry']:
            if 'value' in log:
                val[log['name']] = log['value']
            else:
                val[log['name']] = 0.0
        feat_val[hit['_id']] = val
    return response, feat_val

# def get_training_sample_for_one_query(q, qid, feature_set_name, output_file):
def get_training_sample_for_one_query(q, qid, rank, feature_set_name, output_file, host, auth, headers, index_name):
    ori_rank = []
    ids = [i for i in rank]
    _, feat_val = get_func_feat(ids, feature_set_name, q, index_name, host, auth, headers)
    
    # saving map file
    mapping = list(feat_val[list(feat_val.keys())[0]].keys())
    mapping = [[i, mapping[i]] for i in range(len(mapping))]
    mapping_dict = {}
    for m in mapping:
        mapping_dict[m[1]] = str(m[0]+1)
    print(mapping)
    file = open(output_file + '_mapping.txt','w',encoding='utf-8')
    file.write('0 na q' +'\n')
    for i in range(len(mapping)):
        file.write(str(mapping[i][0]+1) + ' ' + mapping[i][1] + ' q' +'\n')
    file.close()
    
    for _id in rank:
        _rank = rank[_id]
        ori_rank.append(str(_rank) + ' '
                        +'qid:' + str(qid) + ' '
                        +' '.join([mapping_dict[key]+':'+str(feat_val[_id][key]) for key in feat_val[_id]])
                        +' # ' + _id + ' ' 
                        + q)

    # saving features file
    file = open(output_file,'a',encoding='utf-8')
    for i in range(len(ori_rank)):
        file.write(str(ori_rank[i])+'\n')
    file.close()
    
    return

def get_training_set(ranks, feature_set_name, output_file, host, auth, headers, index_name):
    i = 0
    for key in ranks:
        get_training_sample_for_one_query(key, i+1, ranks[key], feature_set_name, output_file, 
                                          host, auth, headers, index_name)
        i += 1
    return

def train_xgb(training_sample_file):
    dtrain = xgb.DMatrix(training_sample_file)
    param = {'max_depth':4, 'eta':2, 'silent':2, 
             'objective':'rank:pairwise', 'eval_metric':'ndcg',
            'nthread':4}
    num_round = 10
    bst = xgb.train(param, dtrain, num_round)
    model = bst.get_dump(fmap=training_sample_file + '_mapping.txt', dump_format='json')
    # os.remove(training_sample_file)
    # os.remove(training_sample_file + '_mapping.txt')
    # return "[" + json.dumps(json.loads(model[0])) + "]"
    return json.dumps([json.loads(model[i]) for i in range(len(model))])

def create_model(name, feature_set_name, definition, host, auth, headers):
    r = requests.get(host + '_ltr/_model', auth=auth, headers=headers)
    r = json.loads(r.text)
    exist_models = []
    for ri in r['hits']['hits']:
        exist_models.append(ri['_source']['name'])
    if name in exist_models:
        return name+' was exist'
    
    
#     POST _ltr/_featureset/elevator_features/_createmodel
    create_model_base = {
        "model": {
            "name": "",
            "model": {
                "type": "model/xgboost+json",
                "definition": ''}
        }
    }
    create_model_base['model']['name'] = name
    create_model_base['model']['model']['definition'] = definition
#     print(type(definition), create_model_base)
    r = requests.post(host + '_ltr/_featureset/' + feature_set_name +'/_createmodel', 
                      auth=auth, headers=headers, json=create_model_base)
    return r.text

def handler(event, context):
    print(event)
    dynamodb_region = event['dynamodb']['region']
    # dynamodb = boto3.resource('dynamodb', region_name=dynamodb_region)
    client = boto3.client('dynamodb', region_name=dynamodb_region)
    table_name = event['dynamodb']['table_name']
    before_day = event['dynamodb']['before_day']
    
    datetime = time.time() - before_day*24*60*60

    index_name = event['opensearch']['index_name']
    host = event['opensearch']['host']
    region = event['opensearch']['region']
    auth = (event['opensearch']['username'], event['opensearch']['password'])
    
    headers = { "Content-Type": "application/json" }

    feature_set_name = event['opensearch']['feature_set_name']
    feature_set = json.loads(event['opensearch']['feature_set'])

    training_set_file = '/tmp/training_set.txt'

    model_name = event['opensearch']['model_name']

    # get rank from dynamodb
    items = read_db_with_time(datetime, client, table_name)
    ori_rank = formulate_items(items)
    ori_rank_check = check(ori_rank)
    rank = get_ranking(ori_rank_check)

    # creat feature set
    print(create_feature_set(feature_set_name, feature_set, host, auth, headers))

    # generate training sample set 
    get_training_set(rank, feature_set_name, training_set_file, host, auth, headers, index_name)

    # training using xgboost
    model = train_xgb(training_set_file)
    print(model)

    # deploy the training model to OpenSearch
    r = create_model(model_name, feature_set_name, model, host, auth, headers)
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "isBase64Encoded": False
    }
    response['body'] = r
    return response


if __name__=='__main__':
    event = {
        "dynamodb":{
            "table_name": "",
            "before_day": 3,
            "region": ""
        },
        "opensearch": {
            "host": "",
            "index_name": "",
            "region": "",
            "username": "",
            "password": "",
            "feature_set_name": "",
            "feature_set": "[\"description\", \"detection\"]",
            "model_name": "",
        },
    }

    handler(event, None)