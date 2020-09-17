import ast
import re

VOWELS = 'aeiou'
CONSONANTS = 'bcdfghjklmnpqrstvx'
SEQUENCES = ['qu']
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
            '((?<=\A)({}|[{}])*)?[{}]?({}|[{}])(([{}])*(?![{}]))?'.format(
                '|'.join(SEQUENCES),
                CONSONANTS,
                CONSONANTS,
                '|'.join(DIPTHONGS),
                VOWELS,
                CONSONANTS,
                VOWELS),
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
        for pos, syl in enumerate(self.syllables):
            if pos < len(self.syllables) - 1:
                syl.add_coda_weight(self.syllables[pos + 1].onset_weight())

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
                'I' if syl.is_initial() else '',
                'F' if syl.is_final() else ''
            ), end='')
        print('\n')
        for syl in self.syllables:
            print('  {:<1} {:<1} '.format(
                syl.nucleus_weight(), syl.coda_weight()), end='')
        print('\n')


class Syllable:
    def __init__(self, chars):
        self.chars = chars[:]
        self.slots = []
        self.final = False
        self.initial = False
        nucleus_seen = False
        self.weights = {'onset': 0, 'nucleus': 0, 'coda': 0}
        for pos, c in enumerate(self.chars):
            if c in VOWELS:
                # 'qu' does not fill a nucleus spot
                if c == 'u' and self.chars[pos - 1] in 'qQ':
                    continue
                self.slots.append('V')
                self.add_nucleus_weight()
                nucleus_seen = True
            elif c in CONSONANTS:
                self.slots.append('C')
                if nucleus_seen:
                    self.add_coda_weight()
                else:
                    self.add_onset_weight()
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

    def is_final(self):
        return self.final

    def is_initial(self):
        return self.initial

    def add_onset_weight(self, weight=1):
        self.weights['onset'] += weight

    def add_nucleus_weight(self, weight=1):
        self.weights['nucleus'] += weight

    def add_coda_weight(self, weight=1):
        self.weights['coda'] += weight

    def onset_weight(self):
        return self.weights['onset']

    def nucleus_weight(self):
        return self.weights['nucleus']

    def coda_weight(self):
        return self.weights['coda']

    def print(self):
        print(self.chars)
