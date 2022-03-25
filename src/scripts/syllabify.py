import click
import os
import paths
from datetime import date


def syllabify_file(input_file=None):
    from syllable import Words, SyllabifiedLine
    w = Words(input_file)
    syllabified_lines = []
    for line in w.lines():
        syls = []
        for word in line:
            try:
                for syl in word.to_syllables():
                    syls.append(syl)
            except IndexError:
                print('Unable to syllabify \"{}\", skipping'.format(word.chars))
        syllabified_lines.append(SyllabifiedLine(syls))
    return syllabified_lines


def write_output(syllabified_lines, output_file, scan=False):
    data_file = output_file + '.csv'
    print("Writing output to ", output_file)
    with open(output_file, 'w') as f:
        for s in syllabified_lines:
            f.write(s.string())

    print("Writing data to ", data_file)
    with open(data_file, "w") as d:
        if scan:
            for lineno, s in enumerate(syllabified_lines):
                vals = [lineno + 1, len(s.syllables)]
                for syl in s.syllables:
                    if syl.nucleus_weight() >= 2 or syl.coda_weight() >= 2:
                        vals.append(2)
                    else:
                        vals.append(0)
                d.write('{}\n'.format(','.join(str(v) for v in vals)))
        else:
            for lineno, s in enumerate(syllabified_lines):
                for syl in s.syllables:
                    wp, rwp, lp, rlp = syl.positions()
                    d.write('{},{},{},{},{},{},{},{},{}\n'.format(
                        lineno,
                        syl.chars,
                        syl.nucleus_weight(),
                        syl.coda_weight(),
                        syl.nucleus_class(),
                        wp,
                        rwp,
                        lp,
                        rlp))

@click.command()
@click.option('-a', '--author-index', help='Author index')
@click.option('-w', '--work-index', help='Work index')
@click.option('-c', '--chapter-index', help='Chapter index')
@click.option('-f', '--input-file', help='Local file to process')
@click.option('-o', '--output-file', help='Destination file for output')
@click.option('-s', '--scan', help='Attempt scansion', is_flag=True)
@click.option('-d', '--directory', help='Process directory contents', is_flag=True)
def main(author_index, work_index, chapter_index, input_file, output_file, scan, directory):
    """Process and syllabify/scan text(s)"""
    paths.add_repo_paths()

    if directory:
        chapters_dir = '/'.join(
            [
                'texts/latin',
                author_index,
                work_index
            ])
        for f in os.listdir(chapters_dir):
            syllabified_lines = syllabify_file('/'.join([chapters_dir, f]))
            write_output(syllabified_lines, '/'.join(
                [
                    'datasets/syllabifications',
                    author_index,
                    work_index,
                    f + '.syl'
                ]), scan)
    else:
        syllabified_lines = syllabify_file(input_file)
        write_output(syllabified_lines, output_file, scan)

    return 0


if __name__ == "__main__":
    exit(main())
