import ast
import re

VOWELS = 'aeiouy'
VOWELS_NOT_U = 'aeioy'
CONSONANTS = 'bcdfghjklmnpqrstvxz'
SPECIALS_initial_only = ['\Aia[{}]'.format(CONSONANTS), 'cui', 'huic']
SEQUENCES = ['qu', 'gu']
DIPTHONGS = ['ae', 'oe', 'au', 'ei', 'eu']
CONSONANT_SPECIAL_WEIGHTS = {
    'h': 0,
    'x': 2,
    'z': 2
}

STOPS = 'bcdgpt'
LIQUIDS = 'rl'


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
        self.chars = chars.lower()
        # Replace 'u' standing for 'v' with an actual 'v' - makes
        # syllabification much simpler
        self.chars = re.sub('((?<=[{}]))u(?=[{}][{}])|(?<=\A)u(?=[{}])|(?<![tfqg])u(?=[aeo])|(?<=[{}])u(?=[{}]\Z)'.format(
            VOWELS, VOWELS, CONSONANTS, VOWELS, VOWELS, VOWELS), 'v', self.chars)
        self.chars = re.sub(
                'iu(?=([ugp]|[vn][{}]|ng|st))'.format(VOWELS), 'ju', self.chars)
        self.chars = re.sub('(?<=\A)io', 'jo', self.chars)
        self.chars = re.sub('((?<=o)|(?<=\A))ia', 'ja', self.chars)
        # Take care of Greek names - easiest way is to treat 'y' as a true upsilon
        self.chars = re.sub('(?<=[{}])y(?=[{}])'.format(CONSONANTS, CONSONANTS),
                            'u', self.chars)
        # self.chars = chars
        self.vsp = re.compile(
            # '((?<=\A)({}|[{}])*)?[{}]?({}|[{}])(([{}])*(?![{}]))?'.format(
            '({})|({}|[{}])*[{}]?({}|[{}])(([{}])*(?![{}]))?'.format(
                '|'.join(SPECIALS_initial_only),
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
        syllables[-1].mark_final()
        return syllables


# SyllabifiedLine represents a single line decomposed into Syllable objects,
# stored in order of occurrence within the line
class SyllabifiedLine:
    def __init__(self, syllables):
        self.syllables = syllables
        for pos, syl in enumerate(self.syllables):
            # If we are not the last syllable in the line, then our weight is
            # affected by the next syllable
            if pos < len(self.syllables) - 1:
                next_syl = self.syllables[pos + 1]
                # Handle elision
                if syl.is_final():
                    if next_syl.chars[0] in VOWELS or (
                            next_syl.chars[0] == 'h'
                            and next_syl.chars[1] in VOWELS):
                        if syl.chars[-1] in VOWELS or (
                                syl.chars[-1] == 'm'
                                and syl.chars[-2] in VOWELS):
                            syl.set_zero_weight()
                            continue

                    # Handle stop-liquid sequence across syllable boundary
                if syl.chars[-1] in STOPS and next_syl.chars[0] in LIQUIDS:
                    syl.add_coda_weight(.5)
                else:
                    syl.add_coda_weight(self.syllables[pos + 1].onset_weight())

    def syllable_count(self):
        return len(self.syllables)

    def print(self):
        print(self.string())

    def string(self):
        return '\n'.join([
            ' '.join('{:<7}'.format(syl.chars) for syl in self.syllables),
            ' '.join('{:<7}'.format(''.join(syl.slots))
                     for syl in self.syllables),
            ' '.join('{:<3} {:<3}'.format(
                'I' if syl.is_initial() else '',
                'F' if syl.is_final() else ''
                ) for syl in self.syllables),
            ' '.join('{:<3} {:<3}'.format(
                syl.nucleus_weight(), syl.coda_weight()
                ) for syl in self.syllables)
        ]) + '\n'


class Syllable:
    def __init__(self, chars):
        self.chars = chars[:].lower()
        self.slots = []
        self.final = False
        self.initial = False
        nucleus_seen = False
        self.weights = {'onset': 0, 'nucleus': 0, 'coda': 0}
        for pos, c in enumerate(self.chars):
            if c in VOWELS:
                # 'qu' does not fill a nucleus spot
                if c == 'u' and pos > 0 and self.chars[pos - 1] in 'qg':
                    continue
                self.slots.append('V')
                self.add_nucleus_weight()
                nucleus_seen = True
            elif c in CONSONANTS:
                self.slots.append('C')
                weight = CONSONANT_SPECIAL_WEIGHTS[c] if c in CONSONANT_SPECIAL_WEIGHTS else 1
                if c in LIQUIDS and pos > 0 and self.chars[pos - 1] in STOPS:
                    weight = .5
                if nucleus_seen:
                    self.add_coda_weight(weight)
                else:
                    self.add_onset_weight(weight)
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

    # For handling elision
    def set_zero_weight(self):
        self.weights['nucleus'] = 0
        self.weights['coda'] = 0

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
