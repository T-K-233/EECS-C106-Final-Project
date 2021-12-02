import sounddevice as sd
from scipy.io.wavfile import write

def record(length):
    fs = 44100  # Sample rate
    seconds = length  # Duration of recording
    print("Recording")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    write('live_rec/output.wav', fs, myrecording)  # Save as WAV file 