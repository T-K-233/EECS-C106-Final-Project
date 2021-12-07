from scipy.io import wavfile
from Analyze import Analyzer
import sys
import numpy as np
# import socketcomm as socket
import socket
import json
import re
from Record import record


def output(sound, file_name, sample_rate = 44100):
    wavfile.write(file_name, sample_rate, sound)


def construct_note(frequency, length, amplitude=4096, sample_rate=44100):
    try:
        time_points = np.linspace(0, length, int(length*sample_rate))
    except:
        print(frequency, length, length*sample_rate, int(length*sample_rate))
        raise Exception('Failed')
    d = np.sin(2*np.pi*frequency*time_points) if frequency else np.zeros(len(time_points))
    d = amplitude*d
    return d

def construct_sound(arr, sample_rate=44100):
    length = []
    notes = []
    # print()
    # print(arr)
    for note, duration in arr:
        sound = construct_note(0, duration[0][0], sample_rate)
        for j in range(len(duration) - 1):
            rest = duration[j+1][0] - (duration[j][0] + duration[j][1])
            sound = np.append(sound, construct_note(note[2], duration[j][1], sample_rate))
            sound = np.append(sound, construct_note(0, rest, sample_rate))
        sound = np.append(sound, construct_note(note[2], duration[-1][1], sample_rate))
        notes += [sound]
        length += [len(sound)]
        
    max_len = max(length)
    final_sound = np.pad(notes[0], (0, max_len-len(notes[0])))
    final_sounds = [final_sound]
    for n in notes[1:]:
        final_sound = final_sound + np.pad(n, (0, max_len-len(n)))
        final_sounds += [np.pad(n, (0, max_len-len(n)))]
    return final_sound.astype(np.int16), final_sounds


def to_time_cmds(res):
    correspondng_note_dict = {}
    for i in res:
        correspondng_note_dict[i[0]]  = i[1] 

    values_correspondng_note_dict = (list(correspondng_note_dict.values()))

    note_play = []
    for i in values_correspondng_note_dict:
        for j in i:
            note_play.append(j[0])

    note_play.sort()

    for i in correspondng_note_dict.keys():
        correspondng_note_dict[i] = [item for t in correspondng_note_dict[i] for item in t]

    time = [item for sublist in correspondng_note_dict.values() for item in sublist]


    def Convert(a):
        it = iter(a)
        res_dct = dict(zip(it, it))
        return res_dct

    time_dict = Convert(time)

    def get_key(val):
        for key, value in correspondng_note_dict.items():
            if val == value:
                return key
        return "key doesn't exist"

    final_output = []    
    for i in note_play:
        for j in correspondng_note_dict.values():
            if i in j:
                val = j
                #print(get_key(val)[0]+''+str(get_key(val)[1]) ,': Play at', i, 'second for ', time_dict[i], 'seconds')
                final_output.append((get_key(val)[0]+''+str(get_key(val)[1]), i, time_dict[i]))
    
    final_saying2 = []
    for i in final_output:
        if i not in final_saying2:
            final_saying2.append(i)
    return final_output

def to_string_output(final_output):
    for i in final_output:
	    print('Move servo to '+str(i[0])+' at this '+str(i[1])+' sec.')


def filter_impossible(lst, time_buffer):
    n, o = re.split(r'(?<=\D)(?=\d+$)', lst[0][0])
    e = Analyzer.notes_index[n] + int(o)*12
    n_n, t_s, d = lst[0]
    filtered = [(n_n, t_s, d, 0)] if e <= 70 else [(n_n, t_s, d, 1)] 
    i = 0
    while i < len(lst)-1:
        if lst[i+1][1] - lst[i][1]  < time_buffer:
            i += 1
        else:
            note, octave = re.split(r'(?<=\D)(?=\d+$)', lst[i+1][0])
            encoding = Analyzer.notes_index[note] + int(octave)*12
            note_name, time_stamp, duration = lst[i+1]
            if encoding <= 70:
                filtered += [(note_name, time_stamp, duration, 0)]
            else:
                filtered += [(note_name, time_stamp, duration, 1)]
        i += 1
    return filtered



if __name__ == "__main__":
    """
    Mode 1 is IK mode "python driver.py 1 <recording file>"
    Mode 2 is reconstruction mode "python driver.py 2 <recording file> "
    Mode 3 is recording mode "python driver.py 3"
    Mode 4 is full run "python driver.py 4"
    """

    fps = 30
    frames_per_motion = 10

    mode = sys.argv[1] 
    if mode == '1' or mode == '2':
        recording_file_name = sys.argv[2]
    else:
        recording_file_name = record()
        

    # extract and segment audio
    analysis = Analyzer(recording_file_name, debugging=True)
    # in real code set reconstruction = False
    result, result_dict = analysis.extract_and_segment(lambda a: a/128, 500, 1200, cluster_length=0.10, reconstruction=True)
    opt = filter_impossible(to_time_cmds(result), 1/fps*frames_per_motion)
    print(opt)
    if mode == '1' or mode == '4':
        # Connecting to server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 50007))
        s.settimeout(10)
        print("server connected")

        with s:
            received = False 
            sending = False
            while not received:
                #receive dum data
                try:
                    s.sendall(b'note')
                    data = s.recv(1024)
                    if not data:
                        print("server no data")
                        break
                    print(data)
                    if data == b'START':
                        sending = True
                    if sending:
                        buffer = json.dumps(opt)
                        s.sendall(buffer.encode())
                    data = s.recv(1024)
                    if data == b'ACK':
                        sending = False
                        received = True
                except KeyboardInterrupt:
                    print("stopped sending data.")
                    break

    output_file_name =  recording_file_name[: -4] + 'out' + recording_file_name[-4:]
    track, rec = construct_sound(result, sample_rate=analysis.fs)
    output(track, output_file_name, sample_rate=analysis.fs)
    print()