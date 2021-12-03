import sounddevice as sd
import queue
import numpy
import tempfile
import soundfile as sf
from scipy.io.wavfile import write
import sys



def record():
    # fs = 44100  # Sample rate
    q = queue.Queue()
    fs = 44100

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(indata.copy())
    
    filename = tempfile.mktemp(suffix='.wav', dir='live_rec')

    try:
        with sf.SoundFile(filename, mode='x', samplerate=fs, channels=1) as file:
            with sd.InputStream(samplerate=fs, channels=1, callback=callback):
                print('#' * 80)
                print('press Ctrl+C to stop the recording')
                print('#' * 80)
                print('Recording...')
                while True:
                    file.write(q.get())
    except KeyboardInterrupt:
        print('Recording stopped')
        return filename
