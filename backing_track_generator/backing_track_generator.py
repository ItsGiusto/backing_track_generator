import subprocess
import boto3
from mma_to_song_data_parser import MMAToSongDataParser
from midi_converter.midi_to_audio_converter_interface import MidiToAudioConverterInterface

class BackingTrackGenerator(object):
	ACCESS_KEY = "AKIAJACXBFXZQMUXP7DA"
    def __init__(self):
        pass

    def __get_file_name(self, song_name):
        return song_name.replace(" ", "-")

    def get_slot_value(self, key, slots):
        if key in slots:
            return slots[key]["value"]

    def get_backing_track(self, song_name, slots):

        #parse mma file
        parser = MMAToSongDataParser()
        file_name = self.__get_file_name(song_name)
        mma_file_name = file_name + ".mma"
        file_path = "mma-songs-16.06/{}".format(mma_file_name)
        song_data = parser.parse_mma_file(file_path)

        #make relevant changes
        song_data.num_choruses = self.get_slot_value("NumberOfChoruses", slots)
        song_data.tempo = self.get_slot_value("Tempo", slots)
        song_data.style = self.get_slot_value("Style", slots)

        key = self.get_slot_value("Key", slots)
        if key:
            song_data.transpose(key)

        #write mma file
        song_data.print_mma_file(mma_file_name)

        #make midi file
        mid_file_name = file_name + ".mid"
        mma_command = ['python', 'mma_library/mma.py', '-f', mid_file_name, mma_file_name]
        subprocess.check_call(mma_command)

        #write to S3
        s3 = boto3.resource('s3')
        s3.Bucket('coltrane3').upload_file(mid_file_name, 'hello.txt')

        #make mp3 file
        mp3_file_name = file_name + ".mp3"
        MidiToAudioConverterInterface.get_mp3_file("https://s3.amazonaws.com/coltrane3/{}".format(mid_file_name), mp3_file_name)

        #write to s3


if __name__ == "__main__":
    BackingTrackGenerator().get_backing_track("twelve-bar-blues", {})
