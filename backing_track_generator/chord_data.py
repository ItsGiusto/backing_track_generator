from . import transposer
from . import chordtable

class ChordData(object):
    def __init__(self, root = None, quality = None, repeat_chord = False, bass_note = None, silence = None):
        self.root = root
        self.quality = quality
        self.bass_note = bass_note
        self.repeat_chord = repeat_chord
        self.silence = silence

    def get_transposed_bar(self, num_transposition_steps, new_key):
        new_root = None
        if self.root:
            new_root = transposer.transpose(self.root, num_transposition_steps, new_key)
        new_bass_note = None
        if self.bass_note:
            new_bass_note = transposer.transpose(self.bass_note, num_transposition_steps, new_key)

        return ChordData(new_root, self.quality, self.repeat_chord, new_bass_note, self.silence)

    def get_mma_bar_text(self):
        if self.repeat_chord:
            return "/"
        if self.silence:
            return "z!"
        if self.bass_note:
            return "{}{}/{}".format(self.root, self.quality, self.bass_note)
        return "{}{}".format(self.root, self.quality)

    @classmethod 
    def create_chord_data(cls, chord_string):
        if chord_string == "/":
            return ChordData(repeat_chord = True)
        if chord_string == "z!":
            return ChordData(silence = True)
        
        split_chord = chord_string.split('/')
        bass_note = None
        if len(split_chord) == 2:
            bass_note = split_chord[1]

        top_chord = split_chord[0]
        chord_root, chord_quality = ChordData.find_chord_quality(top_chord)
        return ChordData(root=chord_root, quality=chord_quality, bass_note=bass_note)

    @classmethod
    def find_chord_quality(cls, chord):
        for chord_quality in chordtable.chordlist:
            if chord.endswith(chord_quality):
                potential_chord = chord[:len(chord)-len(chord_quality)]
                if potential_chord in chordtable.roots:
                    return (potential_chord, chord_quality)
        for alias in chordtable.aliases:
            for chord_quality in alias:
                if not chord_quality:
                    continue
                if chord.endswith(chord_quality):
                    potential_chord = chord[:len(chord)-len(chord_quality)]
                    if potential_chord in chordtable.roots:
                        return (potential_chord, chord_quality)

