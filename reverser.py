import sys
import pyaudio
import wave
import numpy as np
from pvrecorder import PvRecorder


#### This script records 4 seconds of audio, reverses the audio
#### and exports a combined track. This makes it ultimately silent.

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 6
RATE = 16000
RECORD_SECONDS = 5

pyaudio_instance = pyaudio.PyAudio()

def GetDevice():
    return 0
    for index, device in enumerate(PvRecorder.get_available_devices()):
        return PvRecorder.get_available_devices()[0]
# find the index of respeaker usb device
def find_device_index():
    

    return GetDevice()


device_index = find_device_index()
if device_index < 0:
    print('No ReSpeaker USB device found')
    sys.exit(1)


stream = pyaudio_instance.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []
rev_frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)

    # convert string to numpy array
    data_array = np.fromstring(data, dtype='int16')
    repulse_array = np.fromstring(data*-1, dtype='int16')
    
    # deinterleave, select 1 channel
    channel0 = data_array[0::CHANNELS]
    channel1 = data_array[1::CHANNELS]*-1
    # convert numpy array to string 
    data = channel0.tostring()
    frames.append(data)
    r_data = channel1.tostring()
    rev_frames.append(r_data)

print("* done recording")

stream.stop_stream()
stream.close()
pyaudio_instance.terminate()

from pydub import AudioSegment

def SaveAudio (name, audio):
    wf = wave.open(f'Audio_Samples/{name}.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio_instance.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(audio))
    wf.close()
    return AudioSegment.from_file(f'Audio_Samples/{name}.wav')
sound1 = SaveAudio("audio", frames)
sound2 = SaveAudio("rev_audio", rev_frames)

combined = sound1.overlay(sound2)

combined.export("Audio_Samples/Combined.wav", format='wav')
