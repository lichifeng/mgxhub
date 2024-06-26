'''Used to communicate with a S3 compatible server'''

import json
import os
from io import BytesIO, IOBase

from minio import Minio
from minio.helpers import ObjectWriteResult

from mgxhub.logger import logger


class S3Adapter:
    '''A representation of a S3 compatible server connection

    endpoint, access_key, secret_key, bucket_name are the required to connect to
    the server. If not provided, a ValueError will be raised.

    Args:
        endpoint (str): The server endpoint
        accesskey (str): The access key
        secretkey (str): The secret key
        region (str): The server region
        bucket (str): The bucket name
        secure (str): The secure connection status
    '''

    _endpoint: str | None = None
    _accesskey: str | None = None
    _secretkey: str | None = None
    _region: str | None = None
    _secure: bool = True
    _bucket: str | None = None
    _virtual_host_style = False
    _client = None
    _set_policy: bool = False

    def __init__(
            self,
            endpoint: str | None = None,
            accesskey: str | None = None,
            secretkey: str | None = None,
            region: str | None = None,
            bucket: str | None = None,
            secure: str = "on",
            setpolicy: bool = False
    ):
        '''Initialize the S3Adapter instance

        Example:
            s3 = S3Adapter(**cfg.s3)
        '''

        self._endpoint = endpoint
        self._accesskey = accesskey
        self._secretkey = secretkey
        self._region = region
        self._bucket = bucket
        self._secure = secure.lower() != "off"
        self._set_policy = setpolicy

        if not self._endpoint or not self._accesskey or not self._secretkey:
            raise ValueError('Missing S3 endpoint || access key || secret key')

        self._client = Minio(self._endpoint,
                             access_key=self._accesskey,
                             secret_key=self._secretkey,
                             region=self._region,
                             secure=self._secure
                             )
        self.set_bucket()

    @property
    def bucket(self) -> str:
        '''The bucket name to be used'''

        return self._bucket

    def set_bucket(self) -> None:
        '''Set the bucket policy to public read'''

        # if self.bucket is blank string, use part before the first dot of endpoint as bucket name
        if not self._bucket:
            self._bucket = self._endpoint.split('.')[0]
            self._virtual_host_style = True

        found = self._client.bucket_exists(self._bucket)
        if not found:
            logger.warning(f'[S3] Creating bucket {self._bucket}')
            self._client.make_bucket(self._bucket)

        if self._set_policy:
            _public_read_policy = {
                "Version": '2012-10-17',
                "Statement": [
                    {
                        "Sid": 'AddPublicReadCannedAcl',
                        "Principal": '*',
                        "Effect": 'Allow',
                        "Action": ['s3:GetObject'],
                        "Resource": [f"arn:aws:s3:::{self._bucket}/*"]
                    }
                ]
            }
            self._client.set_bucket_policy(self._bucket, json.dumps(_public_read_policy))

    def have(self, file_path: str) -> bool:
        '''Check if a file exists in the server.

        Args:
            file_path (str): The file path to check

        Returns:
            bool: True if the file exists, False otherwise
        '''

        try:
            result = self._client.stat_object(self._bucket, file_path)
            return bool(result.etag)
        except Exception as e:
            return False

    def upload(
            self,
            source_file: str | IOBase,
            dest_file: str,
            metadata: dict | None = None,
            content_type: str = 'application/octet-stream'
    ) -> ObjectWriteResult:
        '''Upload a file to the server.

        Args:
            source_file (str | IOBase): The source file path or an IOBase object representing the file
            dest_file (str): The destination file path
            metadata (dict): The metadata to be attached to the file

        Returns:
            ObjectWriteResult: The result of the upload
        '''

        if isinstance(source_file, str):
            return self._client.fput_object(
                self._bucket,
                dest_file, source_file,
                metadata=metadata, content_type=content_type
            )

        source_file.seek(0, os.SEEK_END)
        size = source_file.tell()
        source_file.seek(0)
        return self._client.put_object(
            self._bucket,
            dest_file, source_file, length=size,
            metadata=metadata, content_type=content_type
        )

    def remove_object(self, file_path: str) -> None:
        '''Remove a file from the server.

        Args:
            file_path (str): The file path to remove
        '''

        self._client.remove_object(self.bucket, file_path)
        logger.warning(f'[S3] Removed {file_path} from {self.bucket}')

    def download(self, file_path: str) -> object | None:
        '''Download a file from the server and return a file object.

        Args:
            file_path (str): The file path to download

        Returns:
            object: The downloaded file object
        '''

        try:
            response = self._client.get_object(self._bucket, file_path)
            logger.debug(f'[S3] Downloaded {file_path} from {self.bucket}')
            return BytesIO(response.data)
        except Exception as e:
            logger.error(f'[S3] Download failed: {e}')
            return None
