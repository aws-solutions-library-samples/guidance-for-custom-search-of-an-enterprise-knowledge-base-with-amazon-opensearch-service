import json

def lambda_handler(event, context):
    print(event)

    # Retrieve request parameters from the Lambda function input:
    headers = event['headers']
    # queryStringParameters = event['queryStringParameters']
    # stageVariables = event['stageVariables']
    # requestContext = event['requestContext']

    # Parse the input for the parameter values
    tmp = event['methodArn'].split(':')
    apiGatewayArnTmp = tmp[5].split('/')
    awsAccountId = tmp[4]
    region = tmp[3]
    ApiId = apiGatewayArnTmp[0]
    stage = apiGatewayArnTmp[1]
    route = apiGatewayArnTmp[2]

    # Perform authorization to return the Allow policy for correct parameters
    # and the 'Unauthorized' error, otherwise.

    authResponse = {}
    condition = {}
    # now pass all requests
    response = generateAllow('me', event['methodArn'])
    return json.loads(response)

    # 只允许指定的IP地址访问
    # allowed_ip = "111.197.239.14"  # 替换为你想要允许的IP地址/CIDR范围
    

    # if (headers['auth'] == 'allowed_ip'):
    #     # "headerValue1" and queryStringParameters["QueryString1"] == "queryValue1"):
    #     if headers['X-Forwarded-For'] == '111.197.239.14':
    #         response = generateAllow('me', event['methodArn'])
    #         print('authorized')
    #         return json.loads(response)
    #     else:
    #         print('unauthorized IP address')
    #         return 'unauthorized'
    # else:
    #     print('unauthorized')
    #     return 'unauthorized'

# Help function to generate IAM policy
def generatePolicy(principalId, effect, resource):
    authResponse = {}
    authResponse['principalId'] = principalId
    if effect and resource:
        policyDocument = {}
        policyDocument['Version'] = '2012-10-17'
        policyDocument['Statement'] = []
        statementOne = {}
        statementOne['Action'] = 'execute-api:Invoke'
        statementOne['Effect'] = effect
        statementOne['Resource'] = resource
        policyDocument['Statement'] = [statementOne]
        authResponse['policyDocument'] = policyDocument

    authResponse_JSON = json.dumps(authResponse)

    return authResponse_JSON

def generateAllow(principalId, resource):
    return generatePolicy(principalId, 'Allow', resource)

def generateDeny(principalId, resource):
    return generatePolicy(principalId, 'Deny', resource)

