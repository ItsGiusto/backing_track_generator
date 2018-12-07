from backing_track_generator.mma_to_song_data_parser import MMAToSongDataParser
from backing_track_generator.backing_track_generator import BackingTrackGenerator

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

parser = MMAToSongDataParser()
song_data = parser.parse_mma_file("mma-songs-16.06/autumn-leaves.mma")


song_data.transpose('F')
song_data.tempo = 150
song_data.num_choruses = 5

print(var_dump(song_data))


song_data.print_mma_file('s.mma')
