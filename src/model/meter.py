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

#
# End meter class definitions
#

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
def main(meter_name, show_syllable_count):
    """Get details about available/known meters"""

    if meter_name:
        click.echo("Meter: {}".format(meter_name))
        click.echo("")
        for p in get_meter(meter_name).patterns():
            click.echo('{}{:>30}'.format(p, " Syllable count: {}".format(len(p)) if show_syllable_count else ""))

if __name__ == "__main__":
    exit(main())