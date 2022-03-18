from ibm_boto3.session import Session
from ibm_botocore.client import Config
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

    def watch_bucket(self, bucket_name=None):
        cos = self.session.resource(
            service_name='s3',
            endpoint_url=self.cos_endpoint,
            config=Config(signature_version='oauth')
        )

        obj_iter = cos.Bucket(bucket_name).objects.all()
        for obj in obj_iter:
            print(obj)
