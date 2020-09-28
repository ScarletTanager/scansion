import requests
import argparse
import os
from datetime import date
import paths

TEXT_URL = 'http://latin-texts.{}.svc.cluster.local/{}/{}/{}.txt'
NS_FILE = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'


def get_text(author, work, chapter):
    from text import Text

    # headers = {'user-agent': 'curl/7.64.1'}
    with open(NS_FILE) as f:
        namespace = f.read()
        request_path = TEXT_URL.format(namespace, author, work, chapter)
        try:
            r = requests.get(request_path)
            if r.status_code != 200:
                print('Received {} from server'.format(r.status_code))
                return None
        except ConnectionError:
            print('Unable to connect to server at {}'.format(request_path))
            return None

        with open('/tmp/' + '-'.join([
                author,
                work,
                chapter]) + '.txt', 'w+') as tmp_file:
            tmp_file.write(r.text)
            tmp_file.seek(0)
            return Text(tmp_file)


def upload_processed_text(text, name,
                          cos, bucket_name):
    # Write to a temp file
    tmp_file = os.path.join('/tmp', name)
    with open(tmp_file, 'w') as f:
        for line in text.lines:
            f.write('[\'' + '\',\''.join(line) + '\']' + '\n')

    cos.put_text(
        bucket_name=bucket_name,
        file=tmp_file)


def main():
    paths.add_repo_paths()
    from cos import CloudObjectStorage

    parser = argparse.ArgumentParser(
        description='Download and parse Latin texts',
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

    args = parser.parse_args()

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
        print('Using COS for text storage.')
        if not cos_instance_id or not bucket or not iam_endpoint or not api_key:
            print('Missing one or more required parameters for using COS.')
            return -1

    text = get_text(author_index, work_index, chapter_index)

    if cos_endpoint:
        upload_file_name = '-'.join([
            date.today().isoformat(),
            author_index,
            work_index,
            chapter_index]) + '.text'
        print('Uploading file {} to COS...'.format(upload_file_name))
        upload_processed_text(
                text=text,
                name=upload_file_name,
                bucket_name=bucket,
                cos=CloudObjectStorage(
                    api_key=api_key,
                    instance_id=cos_instance_id,
                    iam_endpoint=iam_endpoint,
                    cos_endpoint=cos_endpoint))
    else:
        text.print()

    return 0


if __name__ == "__main__":
    exit(main())
