import argparse
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


def main():
    paths.add_repo_paths()

    parser = argparse.ArgumentParser(
        description='Syllabify latin texts',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--author-index',
                        required=False, help='Author index')
    parser.add_argument('-w', '--work-index',
                        required=False, help='Work index')
    parser.add_argument('-c', '--chapter-index',
                        required=False, help='Chapter index')
    parser.add_argument('-f', '--input-file',
                        required=False, help='Local file to process')
    parser.add_argument('-o', '--output-file',
                        required=False, help='Destination file for output')
    parser.add_argument('-s', '--scan', choices=['true', 'false', 't', 'f'],
                        required=False, help='Attempt scansion')
    parser.add_argument('-d', '--directory', choices=['true', 'false', 't', 'f'],
                        required=False, help='Process directory contents')

    args = parser.parse_args()

    # Process arguments related to the work to be downloaded
    chapter_index = args.chapter_index if args.chapter_index else os.environ.get(
        'JOB_INDEX')
    author_index = args.author_index if args.author_index else os.environ.get(
        'AUTHOR_INDEX')
    work_index = args.work_index if args.work_index else os.environ.get(
        'WORK_INDEX')

    if args.scan in ['t', 'true']:
        scan = True
    else:
        scan = False

    if args.directory:
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
        syllabified_lines = syllabify_file(args.input_file)
        write_output(syllabified_lines, args.output_file, scan)

    return 0


if __name__ == "__main__":
    exit(main())
