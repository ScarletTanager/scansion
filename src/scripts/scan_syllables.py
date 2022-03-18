import argparse
import paths


def main():
    paths.add_repo_paths()
    import dataset

    parser = argparse.ArgumentParser(
        description='Run model to analyze syllabic data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--data-file',
                        required=True, help='Path to the data file')
    parser.add_argument('-t', '--targets-file',
                        required=True, help='Path to the targets file')
    parser.add_argument('-a', '--test-data-file',
                        required=False, help='Path to test data file')
    parser.add_argument('-g', '--test-target-file',
                        required=False, help='Path to the test targets file')
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
    parser.add_argument('-o', '--output-file',
                        required=False, help='Output file for writing model results')

    args = parser.parse_args()

    ds = dataset.load_latin_dataset(
        data_file_name=args.data_file,
        target_file_name=args.targets_file)

    srs = int(args.split_random_state) if args.split_random_state else 0
    num_estimators = int(args.estimators) if args.estimators else 100
    lr = float(args.learning_rate) if args.learning_rate else 0.1
    md = int(args.max_depth) if args.max_depth else 3
    mf = int(args.max_features) if args.max_features else dataset.data.shape[1]
    mrs = int(args.model_random_state) if args.model_random_state else 0

    tds = None
    if args.test_data_file and args.test_target_file:
        tds = dataset.load_latin_dataset(
            data_file_name=args.test_data_file,
            target_file_name=args.test_target_file
        )

    train_score, test_score, final_result_set = dataset.run_gbc(
        dataset=ds,
        split_random_state=srs,
        n_estimators=num_estimators,
        learning_rate=lr,
        max_depth=md,
        max_features=mf,
        model_random_state=mrs,
        test_dataset=tds)

    if args.output_file:
        with open(args.output_file, 'w') as of:
            for res in final_result_set:
                of.write('{}\n'.format(','.join(res[:])))
    print('Model params\n============\n')
    print('Estimators: {}\tLearning Rate: {}\tMax depth: {}\tMax features: {}\n'.format(
        num_estimators, lr, md, mf))
    print('Random states - Model: {}\tData split{}\n'.format(
        mrs, srs))
    print('Train score: {:.3f}\nTest score: {:.3f}'.format(
        train_score, test_score))


if __name__ == "__main__":
    exit(main())
