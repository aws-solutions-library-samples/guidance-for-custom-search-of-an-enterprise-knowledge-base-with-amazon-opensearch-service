import json
import boto3
import base64
import os
import io
import codecs
import wave
import re
import tempfile


s3 = boto3.client('s3')
sagemaker_client = boto3.client('sagemaker-runtime')

# Create an Amazon SageMaker client
# Your SageMaker Whisper endpoint name
# ASR_ENDPOINT_NAME = 'huggingface-asr-whisper-large-v2'
ASR_ENDPOINT_NAME = os.environ.get('asr_endpoint_name')
 
def lambda_handler(event, context):
    # Get the audio file from the event payload
    # Extract the request body from the event
    request_body = event.get("body")
    
    # Check if the request body is a valid JSON
    try:
        payload = json.loads(request_body)
    except (ValueError, TypeError):
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid request body')
        }
    
    # Extract the "audio" value from the payload
    base64_audio = payload.get("audio")
    if "language" in payload.keys():
        language  = payload.get("language")
    else:
        language  = 'chinese'
    
    # Check if the "audio" value is present and not empty
    if not base64_audio:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing audio data')
        }
    
    # Decode the Base64 audio data
    try:
        audio_data = base64.b64decode(base64_audio)
    except (ValueError, TypeError):
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid Base64 audio data')
        }

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        temp_file.write(audio_data)
        temp_file_path = temp_file.name
        print(temp_file_path)

    with open(temp_file_path, "rb") as file:
        print('in read file')
        wav_file_read = file.read()
    
    payload = {
            "audio_input": wav_file_read.hex(),
            "language": language,
            "task": "transcribe"
        }
    # print(payload)
    # file_like_object = io.BytesIO(audio_data)
    sagemaker_client = boto3.client('sagemaker-runtime')
    response = sagemaker_client.invoke_endpoint(
        EndpointName=ASR_ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps(payload),
    )
    
    transcribed_text = json.loads(response['Body'].read().decode('utf-8')).get('text')[0]
    
    return {
        'statusCode': 200,
        'body': json.dumps(transcribed_text)
    }    
