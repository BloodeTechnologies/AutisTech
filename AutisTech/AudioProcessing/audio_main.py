import os
import numpy as np
from matplotlib import pyplot as plt
import librosa
import pandas as pd

import speech_recognition as sr
from os import path
from pydub import AudioSegment

def print_plot_play(x, Fs, text=''):
    """1. Prints information about an audio signal

    Args:
        x: Input signal
        Fs: Sampling rate of x
        text: Text to print
    """
    print()
    # print('%s Fs = %d, x.shape = %s, x.dtype = %s' % (text, Fs, x.shape, x.dtype))
    # plt.figure(figsize=(8, 2))
    # plt.plot(x, color='gray')
    # plt.xlim([0, x.shape[0]])
    # plt.xlabel('Time (samples)')
    # plt.ylabel('Amplitude')
    # plt.tight_layout()
    # plt.show()

def transcribe_audio(x):
    """Transcribes audio

    Args:
        x (audio file): _description_
    """
    print(x)
    if os.path.exists(x):
        sound = AudioSegment.from_mp3(x)
        sound.export("transcript.wav", format="wav")
        
        AUDIO_FILE = "transcript.wav"
        
        r = sr.Recognizer()
        with sr.AudioFile(AUDIO_FILE) as source:
            audio = r.record(source)
            
            print("Transcription: \n", r.recognize_amazon(audio))
    else:
        print("Cannot find path")
        print(x)