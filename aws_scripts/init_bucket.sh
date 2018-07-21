#!/bin/bash
bucket_name='audio-processing-test'

aws s3api create-bucket \
    --acl private \
    --bucket $bucket_name
