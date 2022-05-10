import itertools
import tkinter as tk
import re
from collections import Counter
from pathlib import Path

# GLOBALS
from tkinter.constants import W

suggested_word = ''
corrected_word = ''


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


def count_triples(txt):
    a, b, c = itertools.tee(txt, 3)
    next(b, None)
    next(c, None)
    next(c, None)
    return ((a, b, c) for a, b, c in zip(a, b, c))


class Corrector:
    def __init__(self):
        parent_dir = Path(__file__).parent
        missp_src = parent_dir / 'data' / 'missp.txt'
        missp = open(missp_src).read().split('$')

        bigrams_src = parent_dir / 'data' / 'count_2l.txt'
        self.bigrams = list(line.split()[0] for line in open(bigrams_src).readlines())

        self.word = ''

        self.missp_list = []
        for i in range(len(missp)):
            self.missp_list.append(missp[i].split())

    def set_word(self, txt):
        words = txt.split()
        if words:
            self.word = words[-1]

    def correct(self):
        corrections = []
        for i in range(len(self.missp_list)):
            if self.word in self.missp_list[i] and self.word != self.missp_list[i][0]:
                corrections.append(self.missp_list[i][0])

        if not corrections:
            return ''
        else:

            corrections_valued = {}
            for c in corrections:
                for i, b in enumerate(self.bigrams):
                    if b in c:
                        corrections_valued[c] = i

            return max(corrections_valued, key=corrections_valued.get)


class Suggester:
    def __init__(self):
        parent_dir = Path(__file__).parent
        words_src = parent_dir / 'data' / 'big.txt'
        words = open(words_src).read().lower().split()

        self.word_repetition_cutoff = 5

        self.counted_words = Counter(words)
        self.total_words = sum(self.counted_words.values())
        self.words_prob = dict((word, (count / self.total_words)) for word, count in self.counted_words.items())

        self.counted_word_pairs = Counter(count_pairs(words))
        self.counted_word_triples = Counter(count_triples(words))
        self.word_list = []
        self.buffer = ''

    def set_buffer(self, buffer):
        self.buffer = buffer
        self.word_list = self.buffer.split()

    def suggest2(self):
        if self.word_list:
            prev_word = self.word_list[-1].strip().lower()
        else:
            prev_word = ''

        candidates = {}
        for pair in self.counted_word_pairs.keys():
            if prev_word == pair[0]:
                candidates[pair[1]] = self.counted_word_pairs[pair]
        if candidates:
            candidate_values = dict((word, count * self.words_prob[word]) for word, count in candidates.items())
            output = max(candidate_values, key=candidate_values.get)
            if len(self.word_list) > self.word_repetition_cutoff:
                if output in self.word_list[-self.word_repetition_cutoff:]:
                    candidate_values.pop(output)
                    output = max(candidate_values, key=candidate_values.get)
            return output
        else:
            return ''

    def suggest3(self):
        if len(self.word_list) >= 3:
            prev_word_1 = self.word_list[-1].strip().lower()
            prev_word_2 = self.word_list[-2].strip().lower()
        else:
            return ''


        candidates = {}
        for triple in self.counted_word_triples.keys():
            if prev_word_1 == triple[1] and prev_word_2 == triple[0]:
                candidates[triple[2]] = self.counted_word_triples[triple]

        if candidates:
            candidate_values = dict((word, count * self.words_prob[word]) for word, count in candidates.items())
            output = max(candidate_values, key=candidate_values.get)
            if len(self.word_list) > self.word_repetition_cutoff:
                if output in self.word_list[-self.word_repetition_cutoff:]:
                    candidate_values.pop(output)
                    output = max(candidate_values, key=candidate_values.get)
            return output
        else:
            return ''


suggester = Suggester()
corrector = Corrector()
root = tk.Tk()

text = CustomText(root, width=40, height=4)
text.grid(row=0, column=0, columnspan=2)

label = tk.Label(root, anchor='w', justify='left')
label.configure(text='(f1) Prediction: ')
label.grid(row=1, column=0, sticky=W)

label2 = tk.Label(root, anchor='w', justify='left')
label2.configure(text='(f2) Correction: ')
label2.grid(row=1, column=1, sticky=W)


def on_suggest_press(event):
    text.insert('end-1c', f' {suggested_word}')


def on_correct_press(event):
    txt = text.get('1.0', 'end-1c')
    text.delete('1.0', 'end-1c')
    no_last_word = txt.split()
    if no_last_word:
        no_last_word.pop()
        newtxt = ' '.join(no_last_word)
        text.insert('1.0', f'{newtxt} {corrected_word} ')


def on_text_change(event):
    txt = event.widget.get('1.0', 'end-1c')
    suggester.set_buffer(txt)
    corrector.set_word(txt)

    global suggested_word
    global corrected_word

    suggested_word = suggester.suggest3()
    if suggested_word == '':
        suggested_word = suggester.suggest2()

    corrected_word = corrector.correct()

    label.configure(text=f'(f1) Prediction: {suggested_word}')
    label2.configure(text=f'(f2) Correction: {corrected_word}')



text.bind('<<TextModified>>', on_text_change)
root.bind('<F1>', on_suggest_press)
root.bind('<F2>', on_correct_press)

root.mainloop()
