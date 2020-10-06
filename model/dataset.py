from sklearn.utils import Bunch
import numpy as np


def load_latin_dataset(data_file_name, target_file_name):
    dataset = Bunch(
        name='Latin Dataset for Syllabic Analysis',
        feature_names=['nucleus_weight',
                       'coda_weight',
                       'nucleus_class',
                       'word_position',
                       'reverse_word_position',
                       'line_position',
                       'reverse_line_position'],
        target_names=['zero', 'short', 'long']
    )
    data = []
    data_rows_skipped = 0
    with open(data_file_name) as f:
        for line in f:
            feature_vals = line.strip().split(',')
            if len(feature_vals) != 8:
                # Skip the line silently for now
                data_rows_skipped += 1
                continue
            data.append([
                int(feature_vals[1]),
                float(feature_vals[2]),
                int(feature_vals[3]),
                int(feature_vals[4]),
                int(feature_vals[5]),
                int(feature_vals[6]),
                int(feature_vals[7])
            ])
            dataset['data'] = np.array(data)

    target = []
    with open(target_file_name) as f:
        for line in f:
            target.append(int(line.strip()))
        dataset['target'] = np.array(target)

    return dataset
