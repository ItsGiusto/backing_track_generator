from backing_track_generator.mma_to_song_data_parser import MMAToSongDataParser
from backing_track_generator.backing_track_generator import BackingTrackGenerator
import boto3
import os
import subprocess
import json

import types
def var_dump(obj, depth=4, l=""):
    #fall back to repr
    if depth<0: return repr(obj)
    #expand/recurse dict
    if isinstance(obj, dict):
        name = ""
        objdict = obj
    else:
        #if basic type, or list thereof, just print
        canprint=lambda o:isinstance(o, (int, float, str, bool, types.LambdaType))
        try:
            if canprint(obj) or sum(not canprint(o) for o in obj) == 0: return repr(obj)
        except TypeError:
            pass
        #try to iterate as if obj were a list
        try:
            return "[\n" + "\n".join(l + var_dump(k, depth=depth-1, l=l+"  ") + "," for k in obj) + "\n" + l + "]"
        except TypeError:
            #else, expand/recurse object attribs
            name = (hasattr(obj, '__class__') and obj.__class__.__name__ or type(obj).__name__)
            objdict = {}
            for a in dir(obj):
                if a[:2] != "__" and (not hasattr(obj, a) or not hasattr(getattr(obj, a), '__call__')):
                    try: objdict[a] = getattr(obj, a)
                    except Exception: objdict[a] = str(e)
    return name + "{\n" + "\n".join(l + repr(k) + ": " + var_dump(objdict[k], depth=depth-1, l=l+"  ") + "," for k in objdict) + "\n" + l + "}"
'''
parser = MMAToSongDataParser()
song_data = parser.parse_mma_file("mma-songs-16.06/twelve-bar-blues.mma")


song_data.transpose('F')
song_data.tempo = 150
song_data.num_choruses = 5

print(var_dump(song_data))


song_data.print_mma_file('s.mma')

s3 = boto3.resource('s3')
print("Uploading to S3")
s3.Bucket('alexafakebook').upload_file('s.mma', 's.mma', ExtraArgs={'ACL':'public-read'})
'''
'''
from midi2audio import FluidSynth

FluidSynth('/Users/satrij/Desktop/hackathon12-18/backing_track_mma/fluidsynth_exec/sf.sf2')
FluidSynth().play_midi('/Users/satrij/Desktop/hackathon12-18/backing_track_mma/fluidsynth_exec/s.mid')
'''

#make wav with fluidsynth
'''
wav_file_name =  "sssss.wav"
tmp_wav_file_name = wav_file_name
print("Making wav file {}".format(tmp_wav_file_name))
fluidsynth_command = ['fluidsynth_exec/fluidsynth-mac', '-ni', "fluidsynth_exec/sf.sf2", 's.mid', '-F', tmp_wav_file_name, '-r', '44100']
subprocess.check_call(fluidsynth_command)
'''
if False:
    filenames = os.listdir('song_data')
    songs = {}
    for filename in filenames:
        with open(os.path.join('song_data', filename)) as f:
            data = json.load(f)

        #print(var_dump(data))

        parser = MMAToSongDataParser()
        song_data = parser.parse_song_json(data)
        songs[filename] = song_data
    print(var_dump(songs, depth=7))
else :


    with open(os.path.join('song_data', "autumn_nocturne.json")) as f:
        data = json.load(f)

    #print(var_dump(data))

    parser = MMAToSongDataParser()
    song_data = parser.parse_song_json(data)
    #song_data.transpose("Db")

    print(var_dump(song_data))

    print(song_data.get_mma_file_text())
