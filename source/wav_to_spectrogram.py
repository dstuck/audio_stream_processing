import logging
from os.path import splitext, basename

from wav_streaming_utils import s3_url_to_spectrogram, write_spectrogram_to_s3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

OUTPUT_PREFIX = 'processed_spectrograms'


def handler(event, context):
    s3_bucket, s3_key = get_bucket_key_from_event(event)
    logger.info(event)
    logger.info("s3://{}/{}".format(s3_bucket, s3_key))
    output = process_file(s3_bucket, s3_key)
    return output


def get_bucket_key_from_event(event):
    records = event.get('Records', [])
    assert(len(records)==1)
    s3_json = records[0].get("s3", {})
    bucket = s3_json.get('bucket', {}).get('name')
    key = s3_json.get('object', {}).get('key')
    return bucket, key


def process_file(s3_bucket, s3_key):
    spectrogram_list = s3_url_to_spectrogram(s3_bucket, s3_key)
    s3_out_key = _get_out_key_from_in_key(s3_key)
    write_spectrogram_to_s3(spectrogram_list, s3_bucket, s3_out_key)


def _get_out_key_from_in_key(s3_key):
    base_name = splitext(basename(s3_key))[0]
    return '{}/{}.csv'.format(OUTPUT_PREFIX, base_name)
