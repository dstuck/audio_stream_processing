#!/bin/bash

function_name='wav-to-spectrogram'
bucket_name='audio-processing-test'
zip_file_object_key='lambda_deploy/wav_to_spectrogram.zip'

aws lambda create-function \
    --function-name $function_name \
    --role role-arn \
    --code S3Bucket=$bucket_name,S3Key=$zip_file_object_key \
    --handler wav_to_spectrogram.handler \
    --description "Process wav files into spectrograms" \
    --runtime python3.6 \
    --memory-size 128
