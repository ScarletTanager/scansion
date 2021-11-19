from sklearn.utils import Bunch
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split


def load_latin_scansion_dataset(data_file_name, target_file_name):
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
    raw = []
    data_rows_skipped = 0
    with open(data_file_name) as f:
        for line in f:
            feature_vals = line.strip().split(',')
            if len(feature_vals) != 9:
                # Skip the line silently for now
                data_rows_skipped += 1
                continue
            try:
                data.append([
                    int(feature_vals[2]),
                    float(feature_vals[3]),
                    int(feature_vals[4]),
                    int(feature_vals[5]),
                    int(feature_vals[6]),
                    int(feature_vals[7]),
                    int(feature_vals[8])
                ])
                raw.append([
                    int(feature_vals[0]),
                    feature_vals[1]])
            except ValueError:
                data_rows_skipped += 1
                print('Bad line: {}'.format(line))

    dataset['data'] = np.array(data)
    dataset['raw'] = np.array(raw)

    target = []
    with open(target_file_name) as f:
        for line in f:
            target.append(int(line.strip()))
        dataset['target'] = np.array(target)

    return dataset

# load_latin_meter_dataset loads a dataset for classifying poems by meter


def load_latin_meter_dataset(data_file_name, target_file_name):
    dataset = Bunch(
        name='Latin Dataset for Metric Classification',
        feature_names=['syllable_count', 'definite_long_count'],
        target_names=[
            'Hendecasyllabics',
            'Dactyllic Hexameter',
            'Choliambics',
            'Elegiac Couplets',
            'Dactyllic Pentameter',
            'Glyconic',
            'Pherecratean',
            'First Asclepiadean',
            'Other'
        ]
    )
    data = []
    raw = []
    data_rows_skipped = 0
    with open(data_file_name) as f:
        for line in f:
            feature_vals = line.strip().split(',')
            if len(feature_vals) != 4:
                # Skip the line silently for now
                data_rows_skipped += 1
                continue
            try:
                data.append([
                    float(feature_vals[2]),
                    float(feature_vals[3])
                ])
                raw.append([
                    int(feature_vals[0]),
                    feature_vals[1]])
            except ValueError:
                data_rows_skipped += 1
                print('Bad line: {}'.format(line))

    dataset['data'] = np.array(data)
    dataset['raw'] = np.array(raw)

    target = []
    with open(target_file_name) as f:
        for line in f:
            target.append(int(line.strip()))
        dataset['target'] = np.array(target)

    return dataset


def run_gbc(dataset, split_random_state, n_estimators, learning_rate, max_depth, max_features, model_random_state, test_dataset=None):
    # for now we're still working with a training dataset.
    # TODO: Update to use unseen data
    X_train, X_test, y_train, y_test = train_test_split(
        np.append(dataset.raw, dataset.data, 1),
        dataset.target,
        random_state=split_random_state)

    if test_dataset:
        X_train = np.append(dataset.raw, dataset.data, 1)
        y_train = dataset.target

        X_test = np.append(test_dataset.raw, test_dataset.data, 1)
        y_test = test_dataset.target

    gbc = GradientBoostingClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        max_features=max_features,
        random_state=model_random_state)

    gbc.fit(X_train[:, 2:], y_train)
    data_with_predictions = np.append(
        X_test,
        np.reshape(gbc.predict(X_test[:, 2:]), (-1, 1)), 1)
    data_with_preds_and_probabilities = np.append(
        data_with_predictions, gbc.predict_proba(X_test[:, 2:]), 1)

    return gbc.score(X_train[:, 2:], y_train), gbc.score(X_test[:, 2:], y_test), data_with_preds_and_probabilities
