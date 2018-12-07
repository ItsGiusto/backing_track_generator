import requests
import os
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class MidiToAudioConverterInterface(object):
    def __init__(self):
        pass

    @classmethod
    def get_mp3_file(cls, midi_s3_url, output_file_location):
        file_name_without_periods = os.path.basename(midi_s3_url).replace(".", "")
        params1 = (
            ('url', midi_s3_url),
            ('input_format', '/[\'MID\',\'MIDI\'/]'),
        )
        print("Sending url {} to conversion service".format(midi_s3_url))
        response1 = requests.get('https://ct3.ofoct.com/upload_from_url.php', params=params1, verify=False)


        print("Response: {}".format(response1))
        print("Text: {}".format(response1.text.encode('ascii', 'ignore').decode('ascii')))
        job_id1 = MidiToAudioConverterInterface.capture_regex('0\|SUCCESS\|(.+).mid\|mid\|', response1.text)
        file_name_without_periods = MidiToAudioConverterInterface.capture_regex('0\|SUCCESS\|.+.mid\|mid\|(.+)', response1.text)

        params2 = (
            ('cid', 'midi2audio'),
            ('output', 'MP3,WAV,OGG,AAC,WMA'),
            ('tmpfpath', '{}.mid'.format(job_id1)),
            ('row', 'file1'),
            ('sourcename', file_name_without_periods),
            ('outformat', 'mp3'),
            ('AudioQuality', '19'),
            ('AudioEncoder', '1'),
            ('AudioSamplingRate', '11'),
            ('AudioChannels', '1'),
            ('rowid', 'file1'),
        )

        print("Initiating conversion of {}".format(job_id1))
        response2 = requests.get('https://ct3.ofoct.com/convert-file_v2.php', params=params2, verify=False)
        print("Response: {}".format(response2))
        print("Text: {}".format(response2.text.encode('ascii', 'ignore').decode('ascii')))
        job_id2 = MidiToAudioConverterInterface.capture_regex('file1\|SUCCESS\|/tmp/(.+).mid.mp3\|.mp3\|{}.mp3\|'.format(file_name_without_periods), response2.text)

        params3 = (
            ('type', 'get'),
            ('genfpath', '/tmp/{}.mid.mp3'.format(job_id2)),
            ('downloadsavename', '{}.mp3'.format(file_name_without_periods)),
        )
        print("Getting file from {}".format(job_id2))
        response3 = requests.get('https://ct3.ofoct.com/get-file.php', params=params3, verify=False)
        print("Response: {}".format(response3))
        open(output_file_location, 'wb').write(response3.content)

        print("File written to: {}".format(output_file_location))


    @classmethod
    def capture_regex(cls, expression, search_string, rule=re.IGNORECASE):
        match = re.search(expression, search_string, rule)
        if match:
            return match.group(1)

if __name__ == "__main__":
    MidiToAudioConverterInterface.get_mp3_file("https://s3.amazonaws.com/coltrane3/ssssss.mid", '/Users/satrij/Desktop/hackathon12-18/backing_track_mma/midi_converter/output.mp3')