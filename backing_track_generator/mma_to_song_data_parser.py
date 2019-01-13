import re
import json
from .chord_data import ChordData
from .song_data import SongData
from .bar_data import BarData

class MMAToSongDataParser(object):

    STYLE_TO_TEMPO = {"afro":110,
    "ballad":60,
    "bossa nova":140,
    "even 8ths":140,
    "funk":140,
    "latin":180,
    "medium swing":100,
    "medium up swing":160,
    "rock pop":115,
    "samba":200,
    "slow swing":80,
    "up tempo swing":240,
    "waltz":100}

    def __init__(self):
        pass

    def parse_mma_file(self, filename):
        file_contents = self.__read_file_to_string(filename)
        default_tempo = self.__capture_regex("tempo\s*(\d+)\s*", file_contents)
        default_key = self.__capture_regex("keysig\s*([^\s]+).*", file_contents)
        title = self.__capture_regex("//\s*(.+)\s*", file_contents)
        default_style = self.__capture_regex_excluding("Groove\s*(.+)\s*", file_contents, ["metronome2-4"])
        default_bars = self.__get_bars(file_contents)

        return SongData(title, "composer", "time_signature", default_tempo, None,
             default_style, None, default_key, None, 3, None, default_bars, None)

    def parse_song_json(self, song_data_filename):
        with open(song_data_filename) as f:
            song_data = json.load(f)
        title = song_data["title"]
        composer = song_data["artist"]
        default_style = "SwingWalk"#song_data["style"]
        default_tempo = MMAToSongDataParser.STYLE_TO_TEMPO[song_data["style"].lower()]
        default_key = song_data["key"].strip("-")
        time_signature = "{}/{}".format(song_data["chartData"][0]["numerator"], song_data["chartData"][0]["denominator"])
        default_bars = self.__get_json_bars(song_data)

        return SongData(title, composer, time_signature, default_tempo, None,
             default_style, None, default_key, None, 3, None, default_bars, None)

    def __get_json_bars(self, song_data):
        bars = []
        for json_bar in song_data["chartData"]:
            bar = BarData()
            prev_chord = None
            for chord_text in json_bar["barData"]:
                chord = ChordData.create_chord_data(chord_text, prev_chord)
                bar.chords_per_beat.append(chord)
                prev_chord = chord
            if "denominator" in json_bar or "numerator" in json_bar:
                time_signature = "{}/{}".format(json_bar["numerator"], json_bar["denominator"])
                bar.time_signature_change = time_signature
            if "section" in json_bar:
                bar.rehearsal_mark = json_bar["section"]
            if "startBarline" in json_bar and json_bar["startBarline"] == "{":
                bar.begin_bar_repeat = True
            if "endBarline" in json_bar and json_bar["endBarline"] == "}":
                bar.end_bar_repeat = True
            if "timeBar" in json_bar:
                bar.ending_numbers.append(json_bar["timeBar"])
            bars.append(bar)
        return bars


    def __get_bars(self, file_contents):
        bars = []
        for line in file_contents.split('\n'):
            match = self.__capture_regex("^\d+\s+(.+)\s*$", line)
            if match:
                chords_texts = match.strip().split()
                bar = BarData()
                for chord_text in chords_texts:
                    chord = ChordData.create_chord_data(chord_text)
                    bar.chords_per_beat.append(chord)
                bars.append(bar)
        return bars

    def __read_file_to_string(self, filename):
        with open(filename, 'r') as file:
            file_contents = file.read()
        return file_contents

    def __capture_regex(self, expression, search_string, rule=re.IGNORECASE):
        match = re.search(expression, search_string, rule)
        if match:
            return match.group(1)

    def __capture_regex_excluding(self, expression, search_string, exclude_strings, rule=re.IGNORECASE):
        matches = re.findall(expression, search_string, rule)
        for match in matches:
            if match.lower() in exclude_strings:
                continue;
            return match
