from sklearn.utils import Bunch
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split


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
    raw = []
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
            raw.append([feature_vals[0]])

    dataset['data'] = np.array(data)
    dataset['raw'] = np.array(raw)

    target = []
    with open(target_file_name) as f:
        for line in f:
            target.append(int(line.strip()))
        dataset['target'] = np.array(target)

    return dataset


def run_gbc(dataset, split_random_state, n_estimators, learning_rate, max_depth, max_features, model_random_state):
    # for now we're still working with a training dataset.
    # TODO: Update to use unseen data
    X_train, X_test, y_train, y_test = train_test_split(
        np.append(dataset.raw, dataset.data, 1),
        dataset.target,
        random_state=split_random_state)

    gbc = GradientBoostingClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        max_features=max_features,
        random_state=model_random_state)

    gbc.fit(X_train[:, 1:], y_train)
    data_with_predictions = np.append(
        X_test,
        np.reshape(gbc.predict(X_test[:, 1:]), (-1, 1)), 1)
    data_with_preds_and_probabilities = np.append(
        data_with_predictions, gbc.predict_proba(X_test[:, 1:]), 1)

    return data_with_preds_and_probabilities
