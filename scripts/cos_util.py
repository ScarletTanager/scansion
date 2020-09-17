import paths
import argparse
import json
import sys


def main():
    paths.add_repo_paths()
    from cos import CloudObjectStorage

    parser = argparse.ArgumentParser(
            description='Obtain ResponseMetadata from COS',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-k', '--api-key', required=True,
                        help='IBM COS api key')
    parser.add_argument('-a', '--account-id', required=True,
                        help='IBM COS account id')
    parser.add_argument('-e', '--endpoint', required=True,
                        help='cos endpoint')
    parser.add_argument('-i', '--iam-endpoint', required=True,
                        help='IAM endpoint')
    parser.add_argument('-b', '--bucket', help='COS bucket name')
    parser.add_argument('-t', '--action', required=True,
                        help='COS action')
    parser.add_argument('-f', '--file', required=False,
                        help='file to to send or get')
    args = parser.parse_args()

    cos = CloudObjectStorage(
        api_key=args.api_key,
        instance_id=args.account_id,
        iam_endpoint=args.iam_endpoint,
        cos_endpoint=args.endpoint
    )

    if args.action == 'put':
        cos.put_text(bucket_name=args.bucket, file=args.file)
    elif args.action == 'get':
        response = cos.get_text(bucket_name=args.bucket, file=args.file)
        print(json.dumps(response, indent=4, default=str))
    else:
        cos.watch_bucket(bucket_name=args.bucket)


if __name__ == '__main__':
    sys.exit(main())
