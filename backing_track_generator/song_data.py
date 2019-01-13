from . import transposer

class SongData(object):
    def __init__(self, title, composer, time_signature, default_tempo, tempo,
     default_style, style, default_key, key, default_num_choruses, num_choruses, default_bars, bars):
        self.title = title
        self.composer = composer
        self.time_signature = time_signature
        self.default_tempo = default_tempo
        self.tempo = tempo
        self.default_style = default_style
        self.style = style
        self.default_key = default_key
        self.key = key
        self.default_num_choruses = default_num_choruses
        self.num_choruses = num_choruses
        
        self.default_bars = default_bars
        self.bars = bars

    def transpose(self, new_key):
        if new_key == self.default_key:
            self.bars = None
            self.key = None
            return
        num_transposition_steps = transposer.get_transponation_steps(self.default_key, new_key)
        self.bars = []
        for bar in self.default_bars:
            self.bars.append(bar.get_transposed_bar(num_transposition_steps, new_key))
        self.key = new_key

    def print_mma_file(self, filename):
        filecontents = self.get_mma_file_text()
        with open(filename, 'w') as file:
            file.write(filecontents)

    def get_mma_file_text(self):
        mma_text = []
        mma_text.append("// {}\n".format(self.title))
        mma_text.append("Tempo {}".format(self.tempo if self.tempo else self.default_tempo))
        mma_text.append("Keysig {}\n".format(self.key if self.key else self.default_key))
        mma_text.append("Groove Metronome2-4")
        mma_text.append("  z * 2\n")
        mma_text.append("Groove {}".format(self.style if self.style else self.default_style))
        mma_text.append("Volume m\n")
        mma_text.append("REPEAT")

        bars_to_use = self.bars if self.bars else self.default_bars
        num_bars = 1
        for i in range(len(bars_to_use)):
            bar = bars_to_use[i]
            next_bar = bars_to_use[i+1] if i+1 < len(bars_to_use) else None
            prev_bar = bars_to_use[i-1] if i > 0 else None
            mma_text.append("{}".format(bar.get_mma_pre_bar_text(prev_bar, next_bar)))
            mma_text.append("{}    {}".format(num_bars, bar.get_mma_bar_text()))
            mma_text.append("{}".format(bar.get_mma_post_bar_text(prev_bar, next_bar)))
            num_bars += 1

        mma_text.append("REPEATEND {}".format(self.num_choruses if self.num_choruses else self.default_num_choruses))
        return "\n".join(mma_text)
