import argparse
import os
import paths
from datetime import date


def download_text(file_name, bucket_name,
                  cos_client=None):
    cos_client.get_text(
        bucket_name=bucket_name,
        file=file_name)


def upload_results(file_name, bucket_name, cos_client=None):
    cos_client.put_text(bucket_name=bucket_name, file=file_name)


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
    parser.add_argument('-o', '--output-file',
                        required=False, help='Destination file for output')

    args = parser.parse_args()

    # Process arguments related to the work to be downloaded
    chapter_index = args.chapter_index if args.chapter_index else os.environ.get(
        'JOB_INDEX')
    author_index = args.author_index if args.author_index else os.environ.get(
        'AUTHOR_INDEX')
    work_index = args.work_index if args.work_index else os.environ.get(
        'WORK_INDEX')

    input_file = args.input_file if args.input_file else '-'.join(
        [
            date.today().isoformat(),
            author_index,
            work_index,
            chapter_index
        ]) + '.text'
    output_file = args.output_file if args.output_file else '-'.join(
        [
            date.today().isoformat(),
            author_index,
            work_index,
            chapter_index
            ]) + '.syl'
    data_file = '-'.join(
        [
            date.today().isoformat(),
            author_index,
            work_index,
            chapter_index
            ]) + '.csv'

    # Process arguments related to COS and IAM access
    cos_endpoint = args.cos_endpoint if args.cos_endpoint else os.environ.get(
        'COS_ENDPOINT')
    cos_client = None
    if cos_endpoint:
        iam_endpoint = args.iam_endpoint if args.iam_endpoint else os.environ.get(
            'IAM_ENDPOINT')
        api_key = args.api_key if args.api_key else os.environ.get(
            'APIKEY')
        cos_instance_id = args.cos_instance_id if args.cos_instance_id else os.environ.get(
            'COS_INSTANCE_ID')
        bucket = args.bucket if args.bucket else os.environ.get(
            'COS_BUCKET')

        print('Using COS for text retrieval.')
        if not cos_instance_id or not bucket or not iam_endpoint or not api_key:
            print('Missing one or more required parameters for using COS.')
            return -1

        cos_client = CloudObjectStorage(
            api_key=api_key,
            instance_id=cos_instance_id,
            iam_endpoint=iam_endpoint,
            cos_endpoint=cos_endpoint)

        download_text(
            file_name=input_file,
            bucket_name=bucket,
            cos_client=cos_client
        )

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

    print("Writing output to ", output_file)
    with open(output_file, 'w') as f:
        for s in syllabified_lines:
            f.write(s.string())

    print("Writing data to ", data_file)
    with open(data_file, "w") as d:
        for s in syllabified_lines:
            for syl in s.syllables:
                d.write('{},{}\n'.format(
                    syl.nucleus_weight(), syl.coda_weight()))

    if cos_client:
        upload_results(
            file_name=output_file,
            bucket_name=bucket,
            cos_client=cos_client
        )
        upload_results(
            file_name=data_file,
            bucket_name=bucket,
            cos_client=cos_client
        )
    return 0


if __name__ == "__main__":
    exit(main())
