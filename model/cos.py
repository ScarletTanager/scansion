from ibm_boto3.session import Session
from ibm_botocore.client import Config
import argparse
import sys
import json
from pathlib import PurePath


class CloudObjectStorage():
    def __init__(self, api_key=None, instance_id=None, iam_endpoint=None,
                 cos_endpoint=None):
        self.cos_endpoint = cos_endpoint
        self.session = Session(
            ibm_api_key_id=api_key,
            ibm_service_instance_id=instance_id,
            ibm_auth_endpoint=iam_endpoint)

    def get_text(self, bucket_name=None, file=None):
        cos = self.session.resource(
            service_name='s3',
            endpoint_url=self.cos_endpoint,
            config=Config(signature_version='oauth')
        )
        response = cos.Bucket(bucket_name).download_file(
            Key=PurePath(file).name,
            Filename=file
        )
        # bucket = cos.bucket(bucket_name)
        # bucket.load()
        return response

    def put_text(self, bucket_name=None, file=None):
        cos = self.session.resource(
            service_name='s3',
            endpoint_url=self.cos_endpoint,
            config=Config(signature_version='oauth')
        )
        cos.Bucket(bucket_name).upload_file(file, PurePath(file).name)


def main():
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
        for bucket in response:
            print(bucket)


if __name__ == '__main__':
    sys.exit(main())
