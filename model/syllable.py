import ast
import re

VOWELS = 'aeiou'
CONSONANTS = 'bcdfghjklmnpqrstvx'
DIPTHONGS = ['ae', 'oe', 'au', 'ei', 'eu', 'ui']


class Words:
    def __init__(self, path):
        with open(path) as f:
            lines = f.read().splitlines()
            self.wordlines = []
            for line in lines:
                self.wordlines.append([Word(n.strip())
                                       for n in ast.literal_eval(line)])

    def lines(self):
        return self.wordlines


class Word:
    def __init__(self, chars):
        self.chars = chars
        self.vsp = re.compile(
            '[{}]?[{}](([{}])*(?![{}]))?'.format(
                CONSONANTS, VOWELS, CONSONANTS, VOWELS),
            flags=re.IGNORECASE)

    # TODO: handle diphthongs
    def to_syllables(self):
        syllables = []
        for syl in self.vsp.finditer(self.chars):
            newSyl = Syllable(syl.group(0))
            newSyl.mark_final(False)
            newSyl.mark_initial(False)
            syllables.append(newSyl)
        syllables[0].mark_initial()
        syllables[len(syllables) - 1].mark_final()
        return syllables


# SyllabifiedLine represents a single line decomposed into Syllable objects,
# stored in order of occurrence within the line
class SyllabifiedLine:
    def __init__(self, syllables):
        self.syllables = syllables

    def syllable_count(self):
        return len(self.syllables)

    # scan_for_meta scans the line for the syllable metadata and marks each
    # syllable accordingly
    # def scan_for_meta(self):

    def print(self):
        for syl in self.syllables:
            print('{:<5} '.format(syl.chars), end='')
        print('\n')
        for syl in self.syllables:
            print('{:<5} '.format(''.join(syl.slots)), end='')
        print('\n')
        for syl in self.syllables:
            print('{:<2} {:<2} '.format(
                'I' if syl.initial else '',
                'F' if syl.final else ''
            ), end='')
        print('\n')


class Syllable:
    def __init__(self, chars):
        self.chars = chars[:]
        self.slots = []
        for c in self.chars:
            if c in VOWELS:
                self.slots.append('V')
            elif c in CONSONANTS:
                self.slots.append('C')
            else:
                self.slots.append('U')

    # Mark the syllable as word-final, default to True

    def mark_final(self, final=True):
        if not final:
            self.final = False
        else:
            self.final = True

    # Mark the syllable as word-initial, default to True
    def mark_initial(self, initial=True):
        if not initial:
            self.initial = False
        else:
            self.initial = True

    def print(self):
        print(self.chars)


if __name__ == "__main__":
    import sys
    w = Words(sys.argv[1])
    syllabified_lines = []
    for l in w.lines():
        syls = []
        for word in l:
            for syl in word.to_syllables():
                syls.append(syl)
        syllabified_lines.append(SyllabifiedLine(syls))
    for s in syllabified_lines:
        s.print()
