import itertools
import tkinter as tk
import re
from collections import Counter
from pathlib import Path

# GLOBALS
suggested_word = ''

# https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback/40618152#40618152
class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + '_orig'
        self.tk.call('rename', self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)

        if command in ('insert', 'delete', 'replace'):
            self.event_generate('<<TextModified>>')

        return result


# adapted from https://stackoverflow.com/questions/54308997/efficient-python-for-word-pair-co-occurrence-counting
def count_pairs(txt):
    a, b = itertools.tee(txt, 2)
    next(b, None)
    return ((a, b) for a, b in zip(a, b))


class Suggester:
    def __init__(self):
        parent_dir = Path(__file__).parent
        words_src = parent_dir / 'data' / 'big.txt'
        words = open(words_src).read().lower().split()

        self.counted_words = Counter(count_pairs(words))
        # max_key = max(self.counted_words, key=self.counted_words.get)
        # print(f'{max_key}: {self.counted_words[max_key]}')
        # print(self.counted_words.keys())
        self.word_list = []
        self.buffer = ''

    def set_buffer(self, buffer):
        self.buffer = buffer
        self.word_list = self.buffer.split()

    def suggest(self):
        if self.word_list:
            prev_word = self.word_list[-1].strip().lower()
        else:
            prev_word = ''

        candidates = {}
        for pair in self.counted_words.keys():
            if prev_word == pair[0]:
                candidates[pair[1]] = self.counted_words[pair]
                return max(candidates, key=candidates.get)

        return ''


suggester = Suggester()
root = tk.Tk()
label = tk.Label(root, anchor='w')
label.configure(text='Suggested word: ')
text = CustomText(root, width=40, height=4)

label.pack(side='bottom', fill='x')
text.pack(side='top', fill='both', expand=True)


def on_suggest_press(event):
    text.insert('end-1c', f' {suggested_word}')


def on_text_change(event):
    txt = event.widget.get('1.0', 'end-1c')
    suggester.set_buffer(txt)

    global suggested_word
    suggested_word = suggester.suggest()

    label.configure(text=f'Suggested word: {suggested_word}')



text.bind('<<TextModified>>', on_text_change)
root.bind('<F1>', on_suggest_press)

root.mainloop()
