import argparse
import paths


def main():
    paths.add_repo_paths()
    import model.dataset as md

    parser = argparse.ArgumentParser(
        description='Run model to analyze syllabic data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--data-file',
                        required=True, help='Path to the data file')
    parser.add_argument('-t', '--targets-file',
                        required=True, help='Path to the targets file')
    parser.add_argument('-e', '--estimators',
                        required=False, help='Number of estimators in the model')
    parser.add_argument('-l', '--learning-rate',
                        required=False, help='Learning rate in the model')
    parser.add_argument('-m', '--max-depth',
                        required=False, help='Maximum tree depth in the model')
    parser.add_argument('-f', '--max-features',
                        required=False, help='Maximum number of features to use when building each estimator')
    parser.add_argument('-r', '--model-random-state',
                        required=False, help='Random state for building model')
    parser.add_argument('-s', '--split-random-state',
                        required=False, help='Random state for splitting dataset between training and test data')

    args = parser.parse_args()

    dataset = md.load_latin_dataset(
        data_file_name=args.data_file,
        target_file_name=args.targets_file)

    srs = args.split_random_state if args.split_random_state else 0
    num_estimators = args.estimators if args.estimators else 100
    lr = args.learning_rate if args.learning_rate else 0.1
    md = args.max_depth if args.max_depth else 3
    mf = args.max_features if args.max_features else dataset.data.shape[1]
    mrs = args.model_random_state if args.model_random_state else 0

    md.run_gbc(
        dataset=dataset,
        split_random_state=srs,
        n_estimators=num_estimators,
        learning_rate=lr,
        max_depth=md,
        max_features=mf,
        model_random_state=mrs)


if __name__ == "__main__":
    exit(main())
