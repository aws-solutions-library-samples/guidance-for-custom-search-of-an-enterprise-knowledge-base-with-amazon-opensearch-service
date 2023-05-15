FROM public.ecr.aws/lambda/python:3.8

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

RUN pip3 install xgboost --target "${LAMBDA_TASK_ROOT}"

RUN pip3 install requests --target "${LAMBDA_TASK_ROOT}"


# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]