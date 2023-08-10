from aws_cdk import (
    Stack,
    CfnParameter,
    Aws,
    Duration,
    aws_lambda as _lambda,
)


def define_lambda_function(function_name,role,timeout = 10 ):
    lambda_function = _lambda.Function(
        function_name = function_name,
        runtime = _lambda.Runtime.PYTHON_3_9,
        role = role,
        code = _lambda.Code.from_asset('../lambda/'+function_name),
        handler = 'lambda_function' + '.lambda_handler',
        timeout = Duration.seconds(timeout),
        reserved_concurrent_executions=50
    )
    return lambda_function