import re
from .chord_data import ChordData
from .song_data import SongData
from .bar_data import BarData

class MMAToSongDataParser(object):
    def __init__(self):
        pass

    def parse_mma_file(self, filename):
        file_contents = self.__read_file_to_string(filename)
        default_tempo = self.__capture_regex("tempo\s*(\d+)\s*", file_contents)
        default_key = self.__capture_regex("keysig\s*(.+)\s*", file_contents).strip()
        title = self.__capture_regex("//\s*(.+)\s*", file_contents).strip()
        default_style = self.__capture_regex_excluding("Groove\s*(.+)\s*", file_contents, ["metronome2-4"]).strip()
        default_bars = self.__get_bars(file_contents)

        return SongData(title, "composer", "time_signature", default_tempo, None,
             default_style, None, default_key, None, 1, None, default_bars, None)


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
