import argparse
import os
import paths
from datetime import date


def main():
    paths.add_repo_paths()
    from syllable import Words, SyllabifiedLine

    parser = argparse.ArgumentParser(
        description='Analyze latin texts for syllablic structure',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--author-index',
                        required=False, help='Author index')
    parser.add_argument('-w', '--work-index',
                        required=False, help='Work index')
    parser.add_argument('-o', '--output-file',
                        required=False, help='Destination file for output')

    args = parser.parse_args()

    # Process arguments related to the work to be processed
    author_index = args.author_index if args.author_index else os.environ.get(
        'AUTHOR_INDEX')
    work_index = args.work_index if args.work_index else os.environ.get(
        'WORK_INDEX')

    output_file = args.output_file if args.output_file else '-'.join(
        [
            date.today().isoformat(),
            author_index,
            work_index
        ]) + '.syl'
    data_file = output_file + '.csv'

    chapters_dir = '/'.join(
        [
            'texts/latin',
            author_index,
            work_index
        ])

    data = []
    for f in os.listdir(chapters_dir):
        w = Words('/'.join([chapters_dir, f]))
        total_syllables = 0
        total_definite_longs = 0
        # Iterate and build the base dataset
        for line in w.lines():
            syls = []
            for word in line:
                try:
                    for syl in word.to_syllables():
                        syls.append(syl)
                except IndexError:
                    print('Unable to syllabify \"{}\", skipping'.format(word.chars))
            total_syllables += len(syls)
            sl = SyllabifiedLine(syls)
            for syl in sl.syllables:
                if syl.coda_weight() > 1 or syl.nucleus_weight() > 1:
                    total_definite_longs += 1

        syls_per_line = total_syllables / len(w.lines())
        definite_longs_per_line = total_definite_longs / len(w.lines())
        try:
            idx = int(f.removesuffix('.txt'))
            data.append([idx, f, syls_per_line, definite_longs_per_line])
        except ValueError:
            print('Unable to extract index from {}\n'.format(f))

    # Sort the data by the index
    data.sort(key=lambda info: info[0])
    print("Writing data to ", data_file)
    with open(data_file, "w") as d:
        for entry in data:
            d.write('{},{},{},{}\n'.format(
                entry[0],
                entry[1],
                entry[2],
                entry[3]
            ))

    return 0


if __name__ == "__main__":
    exit(main())
