import subprocess
import boto3
import os
import uuid
from .mma_to_song_data_parser import MMAToSongDataParser
from midi_converter.midi_to_audio_converter_interface import MidiToAudioConverterInterface


class BackingTrackGenerator(object):

    BUCKET_NAME = "alexafakebook"

    def __init__(self):
        pass

    def __get_file_name(self, song_name):
        return song_name.lower().replace(" ", "-")

    def __get_file_name_underscore(self, song_name):
        return song_name.lower().replace(" ", "_")

    def get_slot_value(self, key, slots):
        if slots.get(key):
            return slots.get(key).value

    def get_musical_key_resolved_value(self, slots):

        slot = slots.get("Key")
        if slot:
            if slot.resolutions:
                toReturn = slot.resolutions.resolutions_per_authority[0].values[0].value.name
                return toReturn
            else:
                return slot.value


    def get_song_resolved_value(self, slots):

        slot = slots.get("SongName")
        if slot:
            if slot.resolutions:
                toReturn = slot.resolutions.resolutions_per_authority[0].values[0].value.name
                return toReturn
            else:
                return slot.value

    def get_backing_track_server(self, slots):
        song_name = self.get_song_resolved_value(slots)
        #parse mma file
        parser = MMAToSongDataParser()
        file_name = self.__get_file_name(song_name)
        mma_file_name = file_name + ".mma"
        tmp_mma_file_name = os.path.join("/tmp",mma_file_name)
        file_path = "mma-songs-16.06/{}".format(mma_file_name)

        print("Loading file from {}".format(file_path))
        song_data = parser.parse_mma_file(file_path)


        #make relevant changes
        song_data.num_choruses = self.get_slot_value("NumberOfChoruses", slots)
        song_data.tempo = self.get_slot_value("Tempo", slots)
        song_data.style = self.get_slot_value("Style", slots)

        key = self.get_musical_key_resolved_value(slots)
        if key:
            song_data.transpose(key)

        #write mma file
        print("Writing file to {}".format(tmp_mma_file_name))
        song_data.print_mma_file(tmp_mma_file_name)

        #make midi file
        mid_file_name = file_name + ".mid"
        tmp_mid_file_name = os.path.join("/tmp",mid_file_name)
        s3_mid_file_name = os.path.join("midi",mid_file_name)
        print("Making midi file {}".format(tmp_mid_file_name))
        mma_command = ['python3', 'mma_library/mma.py', '-f', tmp_mid_file_name, tmp_mma_file_name]
        subprocess.check_call(mma_command)

        #write to S3
        s3 = boto3.resource('s3')
        print("Uploading to S3")
        s3.Bucket(BackingTrackGenerator.BUCKET_NAME).upload_file(tmp_mid_file_name, s3_mid_file_name, ExtraArgs={'ACL':'public-read'})


        #make mp3 file
        mp3_file_name = file_name + ".mp3"
        tmp_mp3_file_name = os.path.join("/tmp",mp3_file_name)
        print("Converting to mp3")
        MidiToAudioConverterInterface.get_mp3_file("https://s3.amazonaws.com/{}/{}".format(BackingTrackGenerator.BUCKET_NAME, s3_mid_file_name), tmp_mp3_file_name)

        s3_mp3_file_name = os.path.join("mp3",mp3_file_name)
        #write to s3
        print("Uploading mp3 to S3")
        s3.Bucket(BackingTrackGenerator.BUCKET_NAME).upload_file(tmp_mp3_file_name, s3_mp3_file_name, ExtraArgs={'ACL':'public-read'})

        return "https://s3.amazonaws.com/{}/{}".format(BackingTrackGenerator.BUCKET_NAME, s3_mp3_file_name)



    def get_backing_track(self, slots):
        song_name = self.get_song_resolved_value(slots)
        #parse mma file
        parser = MMAToSongDataParser()
        song_file_name = self.__get_file_name_underscore(song_name)
        json_file_name = song_file_name + ".json"
        tmp_mma_file_name = os.path.join("/tmp",json_file_name)
        file_path = os.path.join(song_data,json_file_name)

        file_name = str(uuid.uuid4())

        print("Loading file from {}".format(file_path))
        song_data = parser.parse_mma_file(file_path)

        s3 = boto3.resource('s3')

        #make relevant changes
        song_data.num_choruses = self.get_slot_value("NumberOfChoruses", slots)
        song_data.tempo = self.get_slot_value("Tempo", slots)
        song_data.style = self.get_slot_value("Style", slots)

        key = self.get_musical_key_resolved_value(slots)
        if key:
            song_data.transpose(key)

        #write mma file
        print("Writing file to {}".format(tmp_mma_file_name))
        song_data.print_mma_file(tmp_mma_file_name)

        #make midi file
        mid_file_name = file_name + ".mid"
        tmp_mid_file_name = os.path.join("/tmp", mid_file_name)
        if os.path.exists(tmp_mid_file_name):
          print("Removing preexisting file {}".format(tmp_mid_file_name))
          os.remove(tmp_mid_file_name)
        else:
          print("Preexisting file {} does not exist".format(tmp_mid_file_name))
        print("Making midi file {}".format(tmp_mid_file_name))
        mma_command = ['python3', 'mma_library/mma.py', '-f', tmp_mid_file_name, tmp_mma_file_name]
        subprocess.check_call(mma_command)

        #write to s3
        #print("Uploading midi to S3")
        #s3.Bucket(BackingTrackGenerator.BUCKET_NAME).upload_file(tmp_mid_file_name, mid_file_name, ExtraArgs={'ACL':'public-read'})

        '''
        #get sf2 file
        tmp_sf2_file_name = os.path.join("/tmp", "sf.sf2")
        print("Getting {}".format(tmp_sf2_file_name))
        s3.Bucket(BackingTrackGenerator.BUCKET_NAME).download_file('static/sf.sf2', tmp_sf2_file_name)
        '''
        tmp_sf2_file_name = os.path.join("fluidsynth_exec", "sf.sf2")

        #make wav with fluidsynth
        wav_file_name = file_name + ".wav"
        tmp_wav_file_name = os.path.join("/tmp", wav_file_name)

        #fluidsynth -ni -F outstadda2.wav -r 44100 -a file ~/tempstuff/agoodone.sf2 ~/tempstuff/s.mid
        fluidsynth_command = ['fluidsynth_exec/fluidsynth', '-ni', '-F', tmp_wav_file_name, '-r', '22050', '-a', 'file', tmp_sf2_file_name, tmp_mid_file_name]        
        print("Making wav file {} with command: {}".format(tmp_wav_file_name, " ".join(fluidsynth_command)))
        subprocess.check_call(fluidsynth_command)

        #normalize
        normalize_command = ['normalize_exec/normalize', '-a', '0', '--peak', tmp_wav_file_name]        
        subprocess.check_call(normalize_command)

        #write to s3
        #print("Uploading wav to S3")
        #s3.Bucket(BackingTrackGenerator.BUCKET_NAME).upload_file(tmp_wav_file_name, wav_file_name, ExtraArgs={'ACL':'public-read'})

        #make mp3 file
        mp3_file_name = file_name + ".mp3"
        tmp_mp3_file_name = os.path.join("/tmp", mp3_file_name)
        print("Making mp3 file {}".format(tmp_mp3_file_name))
        lame_command = ['lame_exec/lame', '-V', '8', tmp_wav_file_name, tmp_mp3_file_name, '-q', '7', '--nohist', '-b', '16', '-B', '384']
        subprocess.check_call(lame_command)

        s3_mp3_file_name = os.path.join("mp3",mp3_file_name)
        #write to s3
        print("Uploading mp3 to S3")
        s3.Bucket(BackingTrackGenerator.BUCKET_NAME).upload_file(tmp_mp3_file_name, s3_mp3_file_name, ExtraArgs={'ACL':'public-read'})

        return "https://s3.amazonaws.com/{}/{}".format(BackingTrackGenerator.BUCKET_NAME, s3_mp3_file_name)
        

if __name__ == "__main__":
    BackingTrackGenerator().get_backing_track("autumn-leaves", {})
