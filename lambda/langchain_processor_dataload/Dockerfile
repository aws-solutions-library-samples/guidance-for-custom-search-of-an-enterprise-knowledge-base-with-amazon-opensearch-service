FROM public.ecr.aws/lambda/python:3.9
COPY langchain_processor_dataload ${LAMBDA_TASK_ROOT}
COPY langchain_processor_layer/python ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt
CMD [ "lambda_function.lambda_handler" ]
