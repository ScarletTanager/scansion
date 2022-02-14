import itertools

DACTYL = [2, 1, 1]
SPONDEE = [2, 2]
TROCHEE = [2, 1]
IAMB = [1, 2]
DIBRACH = [1, 1]
BACCHIUS = [1, 2, 2]
AMPHIBRACH = [1, 2, 1]
LONGUS = [2]
BREVIS = [1]
CHORIAMB = [2, 1, 1, 2]


def _flatten(p):
    syls = []
    for f in p:
        for s in f:
            syls.append(s)
    return syls


class BaseMeter:
    def __init__(self):
        self.feet = []

    def patterns(self):
        patterns = []
        for raw in list(itertools.product(*self.feet)):
            patterns.append(_flatten(raw))
        return patterns

    # Attempts to match the line to one or more candidate patterns
    # of the specific meter.
    def candidates(self, line, strict=True):
        # Line must be a list of syllables marked as one of
        # 0 (unknown), 1 (short), or 2 (long)
        candidates = []
        for p in self.patterns():
            if len(p) != len(line):
                continue
            for pos, syl in enumerate(line):
                if strict:
                    if syl > 0 and syl != p[pos]:
                        print('Syllable at position {} is {}, expected {}'.format(pos, syl, p[pos]))
                        break
                else:
                    # In non-strict searching, we allow for a syllable which
                    # we preliminarily scanned as short, but the pattern has
                    # a long, because sometimes syllables are long "because the
                    # meter requires it."
                    if syl > p[pos]:
                        print('Syllable at position {} is long, should be short'.format(pos))
                        break
            else:
                print('Pattern: {}'.format(p))
                candidates.append(p)
        return candidates


class DactyllicHexameter(BaseMeter):
    def __init__(self):
        super().__init__()
        self.feet = [
            [DACTYL, SPONDEE],
            [DACTYL, SPONDEE],
            [DACTYL, SPONDEE],
            [DACTYL, SPONDEE],
            [DACTYL, SPONDEE],
            [SPONDEE, TROCHEE]
        ]


class Hendecasyllabics(BaseMeter):
    def __init__(self):
        super().__init__()
        self.feet = [
            [IAMB, SPONDEE, TROCHEE],
            [TROCHEE],
            [IAMB],
            [IAMB],
            [AMPHIBRACH, BACCHIUS]
        ]


class Choliambics(BaseMeter):
    def __init__(self):
        super().__init__()
        self.feet = [
            [IAMB, SPONDEE],
            [IAMB],
            [IAMB, SPONDEE],
            [IAMB],
            [IAMB],
            [IAMB, SPONDEE]
        ]


# Bacause of couplet-based meters, we have to analyze two lines at a time...
class ElegiacCouplets(BaseMeter):
    def __init__(self):
        super().__init__()
        self.feet = DactyllicHexameter().feet
        self.feet.extend([
            [DACTYL, SPONDEE],
            [DACTYL, SPONDEE],
            [DACTYL],
            [TROCHEE],
            [DIBRACH, IAMB]
        ])

# Might be easier if we treat (dactyllic) pentameter as a separate meter...


class DactyllicPentameter(BaseMeter):
    def __init__(self):
        super().__init__()
        self.feet = [
            [DACTYL, SPONDEE],
            [DACTYL, SPONDEE],
            [LONGUS],
            [DACTYL],
            [DACTYL],
            [LONGUS, BREVIS]
        ]


class Glyconic(BaseMeter):
    def __init__(self):
        super().__init__()
        self.feet = [
            [SPONDEE, TROCHEE],
            [CHORIAMB],
            [IAMB]
        ]


class Pherecratean(BaseMeter):
    def __init__(self):
        super().__init__()
        self.feet = [
            [SPONDEE, TROCHEE],
            [CHORIAMB],
            [BREVIS, LONGUS]
        ]


class FirstAsclepiadean(BaseMeter):
    def __init__(self):
        super().__init__()
        self.feet = [
            [SPONDEE],
            [DACTYL],
            [LONGUS],
            [DACTYL],
            [TROCHEE],
            [BREVIS, LONGUS]
        ]
