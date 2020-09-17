import argparse
import os
import paths


def download_text(file_name, bucket_name,
                  cos=None):

    cos.get_text(
        bucket_name=bucket_name,
        file=file_name)


def main():
    paths.add_repo_paths()
    from cos import CloudObjectStorage
    from syllable import Words, SyllabifiedLine

    parser = argparse.ArgumentParser(
        description='Analyze latin texts for syllablic structure',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--author-index',
                        required=False, help='Author index')
    parser.add_argument('-w', '--work-index',
                        required=False, help='Work index')
    parser.add_argument('-c', '--chapter-index',
                        required=False, help='Chapter index')
    parser.add_argument('-b', '--bucket',
                        required=False, help='COS bucket name')
    parser.add_argument('-x', '--cos-instance-id',
                        required=False, help='COS instance ID')
    parser.add_argument('-e', '--cos-endpoint',
                        required=False, help='COS endpoint URL')
    parser.add_argument('-i', '--iam-endpoint',
                        required=False, help='IAM token endpoint')
    parser.add_argument('-k', '--api-key',
                        required=False, help='IAM API key')
    parser.add_argument('-f', '--input-file',
                        required=False, help='Local file to process')

    args = parser.parse_args()

    # if a file is specified, it overrides all other arguments
    if args.input_file:
        w = Words(args.input_file)
        syllabified_lines = []
        for l in w.lines():
            syls = []
            for word in l:
                for syl in word.to_syllables():
                    syls.append(syl)
            syllabified_lines.append(SyllabifiedLine(syls))
        for s in syllabified_lines:
            s.print()
        return 0

    # Process arguments related to the work to be downloaded
    chapter_index = args.chapter_index if args.chapter_index else os.environ.get(
        'JOB_INDEX')
    author_index = args.author_index if args.author_index else os.environ.get(
        'AUTHOR_INDEX')
    work_index = args.work_index if args.work_index else os.environ.get(
        'WORK_INDEX')

    if not author_index or not work_index or not chapter_index:
        print('Must supply the indices for author, work, and chapter.')
        return -1

    # Process arguments related to COS and IAM access
    iam_endpoint = args.iam_endpoint if args.iam_endpoint else os.environ.get(
        'IAM_ENDPOINT')
    api_key = args.api_key if args.api_key else os.environ.get(
        'APIKEY')
    cos_endpoint = args.cos_endpoint if args.cos_endpoint else os.environ.get(
        'COS_ENDPOINT')
    cos_instance_id = args.cos_instance_id if args.cos_instance_id else os.environ.get(
        'COS_INSTANCE_ID')
    bucket = args.bucket if args.bucket else os.environ.get(
        'COS_BUCKET')

    # If the cos endpoint is specified, we assume we're using COS, so we need to
    # have all of the required values, otherwise exit on error
    if cos_endpoint:
        print('Using COS for text retrieval.')
        if not cos_instance_id or not bucket or not iam_endpoint or not api_key:
            print('Missing one or more required parameters for using COS.')
            return -1

    download_text(
        file_name='-'.join([author_index, work_index,
                            chapter_index]) + '.text',
        bucket_name=bucket,
        cos=CloudObjectStorage(
            api_key=api_key,
            instance_id=cos_instance_id,
            iam_endpoint=iam_endpoint,
            cos_endpoint=cos_endpoint)
    )

    w = Words('-'.join([author_index, work_index,
                        chapter_index]) + '.text')
    syllabified_lines = []
    for l in w.lines():
        syls = []
        for word in l:
            for syl in word.to_syllables():
                syls.append(syl)
        syllabified_lines.append(SyllabifiedLine(syls))
    for s in syllabified_lines:
        s.print()

    return 0


if __name__ == "__main__":
    exit(main())
