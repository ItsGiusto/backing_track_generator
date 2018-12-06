from chord_data import ChordData

class BarData(object):
    def __init__(self):
        self.chords_per_beat = []
        self.begin_bar_repeat = False
        self.end_bar_repeat = False
        self.time_signature_change = None
        self.rehearsal_mark = None
        self.ending_numbers = []

    def duplicate(self):
        bar_data = BarData()
        bar_data.begin_bar_repeat = self.begin_bar_repeat
        bar_data.end_bar_repeat = self.end_bar_repeat
        bar_data.time_signature_change = self.time_signature_change
        bar_data.rehearsal_mark = self.rehearsal_mark
        bar_data.ending_numbers = self.ending_numbers
        return bar_data

    def get_transposed_bar(self, num_transposition_steps, new_key):
        new_bar = self.duplicate()
        for chord in self.chords_per_beat:
            new_bar.chords_per_beat.append(chord.get_transposed_bar(num_transposition_steps, new_key))
        return new_bar

    def get_mma_bar_text(self):
        chord_text_list = []
        for chord in self.chords_per_beat:
            chord_text = chord.get_mma_bar_text()
            chord_text_list.append(chord_text)
        return " ".join(chord_text_list)

    def get_mma_pre_bar_text(self):
        if self.begin_bar_repeat:
            return "REPEAT"
        return ""

    def get_mma_post_bar_text(self):
        if self.end_bar_repeat:
            return "REPEATEND"
        return ""