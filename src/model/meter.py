import itertools
import click
import inspect
import sys

# Structural representations of the types of feet found
# across the various meters.
# 2 represents a long syllable, 1 a short one.

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

#
# Below this point you will find class definitions for meters.
# This module should not contain any class which does not
# represent a meter.
#


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
                # print('Pattern length {} does not equal line length {}'.format(len(p), len(line)))
                continue
            for pos, syl in enumerate(line):
                if strict:
                    if syl > 0 and syl != p[pos]:
                        # print('Syllable at position {} is {}, expected {}'.format(pos, syl, p[pos]))
                        break
                else:
                    # In non-strict searching, we allow for a syllable which
                    # we preliminarily scanned as short, but the pattern has
                    # a long, because sometimes syllables are long "because the
                    # meter requires it."
                    if syl > p[pos]:
                        # print('Syllable at position {} is long, should be short'.format(pos))
                        break
            else:
                # print('Pattern: {}'.format(p))
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
# this meter is currently broken
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

class IambicTrimeter(BaseMeter):
    def __init__(self):
        super().__init__()
        self.feet = [
            [IAMB],
            [IAMB],
            [IAMB],
            [IAMB],
            [IAMB],
            [IAMB, DIBRACH]
        ]

class Priapean(BaseMeter):
    def __init__(self):
        super().__init__()
        self.feet = [
            [IAMB, TROCHEE, SPONDEE],
            [TROCHEE],
            [IAMB],
            [IAMB],
            [IAMB, TROCHEE, SPONDEE],
            [TROCHEE],
            [IAMB],
            [LONGUS]
        ]

#
# End meter class definitions
#

#
# metric_probability: provide a percentage possibility of the poem being in the
#   specified meter
#
# returns a dict with these keys:
#   lines_matched_pct: the percentage of lines for which any candidate match was found
#   lines_matched: a list of tuples, one per line.  The 0-index value is a boolean indicating
#       whether any match was found for the line, the 1-index value is the number of candidates
#       for that line
#

def metric_probability(lines, meter_name, strict=True):
    m = get_meter(meter_name)

    matches = []
    lines_matched = 0
    for l in lines:
        candidate_count = len(m.candidates(l, strict))
        found = candidate_count > 0
        if found:
            lines_matched += 1
        matches.append((found, candidate_count))
    return {'lines_matched_pct': lines_matched/len(lines), 'lines_matched': matches}

def __islatinmeter(obj):
    if inspect.isclass(obj) and obj.__name__ != "BaseMeter":
        return True
    return False

def __getmeters():
    meters = {}
    for name, obj in inspect.getmembers(sys.modules[__name__], __islatinmeter):
        meters[name] = obj
    return meters

def list_meters(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    for name in __getmeters().keys():
        click.echo(name)
    ctx.exit()

#
# get_meter: return a new instance of the meter specified by meter_name
#

def get_meter(meter_name):
    meter_class_ = getattr(sys.modules[__name__], meter_name)
    return meter_class_()


@click.command()
@click.option('-l', '--list-meters', help='List available meters',
              is_flag=True, is_eager=True, expose_value=False,
              callback=list_meters)
@click.option('-n', '--meter-name', help='Show details for specified meter',
              type=click.Choice(__getmeters().keys(), case_sensitive=False))
@click.option('-c', '--show-syllable-count', help='Show syllable count for each pattern in meter',
              is_flag=True)
@click.option('-d', '--disable-strict-scanning', help='Disable strictness for matching against meter patterns', is_flag=True)
@click.option('-f', '--filename', help='Syllable file (csv) to process', type=click.Path(exists=True))
def main(filename, meter_name, show_syllable_count, disable_strict_scanning):
    """Get details about available/known meters"""

    if filename:
        scan_strictness = not disable_strict_scanning
        print('Strict scanning enabled: {}'.format(scan_strictness))

        lines = []
        with open(filename) as f:
            for l in f.read().splitlines():
                lines.append([int(syl) for syl in l.split(',')[2:]])
            
            if meter_name:
                mp = metric_probability(lines, meter_name, scan_strictness)
                lines_m = 0
                for lm in mp['lines_matched']:
                    if lm[0]:
                        lines_m += 1
                print('Meter: {:<30} Lines matched: {} out of {}   Match pct: {:.2f}'.format(
                    meter_name, lines_m, len(lines), mp['lines_matched_pct']
                ))
            else:
                for mn in __getmeters().keys():
                    mp = metric_probability(lines, mn, scan_strictness)
                    lines_m = 0
                    for lm in mp['lines_matched']:
                        if lm[0]:
                            lines_m += 1
                    print('Meter: {:<30} Lines matched: {} out of {}   Match pct: {:.2f}'.format(
                        mn, lines_m, len(lines), mp['lines_matched_pct']
                    ))
    elif meter_name:
        click.echo("Meter: {}".format(meter_name))
        click.echo("")
        for p in get_meter(meter_name).patterns():
            click.echo('{}{:>30}'.format(p, " Syllable count: {}".format(len(p)) if show_syllable_count else ""))

if __name__ == "__main__":
    exit(main())