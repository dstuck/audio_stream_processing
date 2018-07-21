import wave
import struct

import boto3
import numpy as np

MAX_FREQUENCY = 800

def s3_url_to_spectrogram(s3_bucket, s3_key):
    f_wav = wave.open(get_file_like_from_s3(
        s3_bucket=s3_bucket,
        s3_key=s3_key
    ))
    spectrum = []
    freqs = get_frequencies_from_wav(f_wav)
    max_index = get_power_spectrum_truncation_index(freqs, MAX_FREQUENCY)
    while True:
        frames = get_frames_from_wav_file(f_wav)
        if frames is None:
            break
        ps = compute_power_spectrum_from_frames(frames)
        spectrum.append(ps[:max_index])
    return spectrum

def get_file_like_from_s3(s3_bucket, s3_key):
    s3_client = boto3.client('s3')
    s3_object = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    return s3_object['Body']

def get_frames_from_wav_file(f_wav, sample_len_seconds=0.1):
    batch_size_frames = get_batch_size_frames(f_wav, sample_len_seconds)
    out_bytes = f_wav.readframes(batch_size_frames)
    if not out_bytes:
        return None
    frames = struct.unpack("<{}h".format(len(out_bytes)//2), out_bytes)
    extra_frames = batch_size_frames - len(frames)
    if extra_frames > 0:
        frames = frames + tuple([0] * extra_frames)
    return frames

def get_batch_size_frames(f_wav, sample_len_seconds=0.1):
    frame_rate = f_wav.getframerate()
    batch_size_frames = int(frame_rate * sample_len_seconds)
    return batch_size_frames


def get_frequencies_from_wav(f_wav, sample_len_seconds=0.1):
    frame_rate = f_wav.getframerate()
    batch_size_frames = get_batch_size_frames(f_wav, sample_len_seconds)
    time_step = 1 / frame_rate
    freqs = np.fft.fftfreq(batch_size_frames, time_step)

    return freqs[freqs >= 0]

def get_power_spectrum_truncation_index(freqs, max_freq):
    if max_freq is None:
        return -1
    return min(np.argwhere(freqs > max_freq))[0]

def compute_power_spectrum_from_frames(frames):
    ft = np.fft.rfft(frames)
    trunc_ft = ft[:int(len(ft)/2)] / len(frames)
    power_spectrum = np.abs(trunc_ft)**2
    return power_spectrum

def write_spectrogram_to_s3(spectrogram, s3_bucket, s3_key):
    client = boto3.client('s3')
    csv_str = '\n'.join([','.join([str(l) for l in line]) for line in spectrogram])
    client.put_object(
        Body=csv_str,
        Bucket=s3_bucket,
        Key=s3_key
    )
