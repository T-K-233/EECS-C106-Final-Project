import sounddevice as sd
import queue
import numpy
import tempfile
import soundfile as sf0
from scipy.io.wavfile import write
import sys



def record(length):
    # # fs = 44100  # Sample rate
    # # seconds = length  # Duration of recording
    # # print("Recording")
    # # myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    # # sd.wait()  # Wait until recording is finished
    # # write('live_rec/output.wav', fs, myrecording)  # Save as WAV file 
    # q = queue.Queue()
    # fs = 44100

    # def callback(indata, frames, time, status):
    #     """This is called (from a separate thread) for each audio block."""
    #     if status:
    #         print(status, file=sys.stderr)
    #     q.put(indata.copy())

    # with sf.SoundFile('live_rec/output.wav', mode='x', samplerate=fs,
    #                   channels=1) as file:
    #     with sd.InputStream(samplerate=fs, channels=1, callback=callback):
    #         print('#' * 80)
    #         print('press Ctrl+C to stop the recording')
    #         print('#' * 80)
    #         while True:
    #             file.write(q.get())


    fs = 44100  # Sample rate
    seconds = length  # Duration of recording
    print("Recording")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    write('live_rec/output.wav', fs, myrecording)  # Save as WAV file 


record(20)