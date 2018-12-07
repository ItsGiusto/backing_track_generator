import subprocess
import boto3
import os
from .mma_to_song_data_parser import MMAToSongDataParser
from midi_converter.midi_to_audio_converter_interface import MidiToAudioConverterInterface

class BackingTrackGenerator(object):
    ACCESS_KEY = "oHzKKaeUDEWNyNCHkDEapAQB4GpIm1QPV+MwsDEg"
    ACCESS_ID = "AKIAJACXBFXZQMUXP7DA"
    def __init__(self):
        pass

    def __get_file_name(self, song_name):
        return song_name.lower().replace(" ", "-")

    def get_slot_value(self, key, slots):
        if slots.get(key):
            return slots.get(key).value

    def get_musical_key_resolved_value(self, slots):
        slot = slots.get("Key")
        if slot:
            toReturn = slot.value

            resolutions = slot.get("resolutions").get("resolutionsPerAuthority")
            if resolutions and len(resolutions > 0):
                values = resolutions[0].get("values")
                if values and len(values > 0):
                    toReturn = resolutions[0].get("value").get("name")

            return toReturn

    def get_backing_track(self, song_name, slots):

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
        print("Making midi file {}".format(tmp_mid_file_name))
        mma_command = ['python3', 'mma_library/mma.py', '-f', tmp_mid_file_name, tmp_mma_file_name]
        subprocess.check_call(mma_command)

        #write to S3
        s3 = boto3.resource('s3', aws_access_key_id= BackingTrackGenerator.ACCESS_ID,
         aws_secret_access_key= BackingTrackGenerator.ACCESS_KEY)
        print("Uploading to S3")
        s3.Bucket('coltrane3').upload_file(tmp_mid_file_name, mid_file_name, ExtraArgs={'ACL':'public-read'})


        #make mp3 file
        mp3_file_name = file_name + ".mp3"
        tmp_mp3_file_name = os.path.join("/tmp",mp3_file_name)
        print("Converting to mp3")
        MidiToAudioConverterInterface.get_mp3_file("https://s3.amazonaws.com/coltrane3/{}".format(mid_file_name), tmp_mp3_file_name)

        #write to s3
        print("Uploading mp3 to S3")
        s3.Bucket('coltrane3').upload_file(tmp_mp3_file_name, mp3_file_name, ExtraArgs={'ACL':'public-read'})

        return "https://s3.amazonaws.com/coltrane3/{}".format(mp3_file_name)

if __name__ == "__main__":
    BackingTrackGenerator().get_backing_track("autumn-leaves", {})
