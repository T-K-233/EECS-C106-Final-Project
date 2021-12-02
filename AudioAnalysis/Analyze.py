import numpy as np
from scipy import signal
from scipy.io import wavfile
import matplotlib.pyplot as plt

rng = np.random.default_rng()



def cluster(arr, dist_thresh, reconstruction=False):
    prev = arr[0]
    time_duration = []
    for i in range(1, len(arr)):
        if arr[i] - arr[i-1] > dist_thresh:
            time_duration += [(prev, arr[i-1]-prev)] if arr[i-1]-prev != 0 else []
            prev = arr[i]
    time_duration += [(prev, arr[-1]-prev)] if arr[-1]-prev != 0 else []
    return time_duration


"""
Class that segments and extract notes from songs
"""
class Analyzer:
    """
    Here defines the mapping of note names to numbers
    """
    notes_chart = {0: 'C',
               1: 'C#',
               2: 'D',
               3: 'D#',
               4: 'E',
               5: 'F',
               6: 'F#',
               7: 'G',
               8: 'G#',
               9: 'A',
               10: 'A#',
               11: 'B'}
               
    notes_index = {'C':0,
                'C#':1,
                'D':2,
                'D#':3,
                'E':4,
                'F':5,
                'F#':6,
                'G':7,
                'G#':8,
                'A':9,
                'A#':10,
                'B':11}

    """
    Here defines the frequency of each note
    """
    notes_freq = 440*(2**(np.arange(-45, 51)/12))

    """
    Constructor for the Analyzer class. 
    - Initiates the data(self.data) to analyze and the sampling frequency(self.fs)
    - Creates spectrogram for analysis

    Parameters:
        recording (string): the file name of the recording for analysis
    """
    def __init__(self, recording):
        self.fs, self.data = wavfile.read(recording)
        self.f, self.t, self.Sxx = signal.spectrogram(self.data.T[0], self.fs, nperseg=self.fs//10) if len(self.data.shape) == 2 else signal.spectrogram(self.data, self.fs, nperseg=self.fs//10)


    """
    Extract and segment function.
    - Extract the notes and figure out when each notes happen
    - Figure out the duration of each note

    Parameters:
        threshold_func (function): the function to determine the power threshold to seperate background noise and audio
        freq_bound_low, freq_bound_high (float): the lowerbound frequency, the upper bound frequency
        reconstruction (boolean): Is the music going to be reconstructed 
    
    Results:
        A List, A dictionary in the following format:
            ('C', 4, 523.2511306011972): <---------------------------Note name (and note frequency, depends on reconstruction)
            [(1.712607709750567, 0.35002267573696155), <-------------Occurence of note and duration
            (15.275986394557822, 0.26251700680272094),
            (25.86417233560091, 1.8376190476190466),
            (51.15331065759637, 2.012630385487526)],
    """
    def extract_and_segment(self, threshold_func, freq_bound_low, freq_bound_high, cluster_length=0.25, reconstruction=False):
        max_energy = np.amax(self.Sxx)
        quiet_threshold = threshold_func(max_energy)
        self.notes_in_song = []
        for n in range(len(Analyzer.notes_freq)):
            i = np.argmin((self.f-Analyzer.notes_freq[n])**2)
            if np.max(self.Sxx[i]) >  quiet_threshold and Analyzer.notes_freq[n] > freq_bound_low and Analyzer.notes_freq[n] < freq_bound_high:
                note_duration = self.t[self.Sxx[i] > quiet_threshold]
                if len(note_duration) > 1:
                    if reconstruction:
                        self.notes_in_song += [((Analyzer.notes_chart[n%12], n//12 + 1, Analyzer.notes_freq[n]), note_duration)]
                    else:
                        self.notes_in_song += [((Analyzer.notes_chart[n%12], n//12 + 1), note_duration)]
        self.result = [(note, cluster(duration, cluster_length, reconstruction)) for note, duration in self.notes_in_song]
        self.result = list(filter(lambda a: len(a[1]) != 0, self.result))
        self.result_dict = {note : cluster(duration, cluster_length, reconstruction) for note, duration in self.notes_in_song}
        return self.result, self.result_dict

