import os
import boto3


class s3Connect:
    """
    Class for lazy connections.
    That is make connections
      a) only when they are needed and then cache them
      b) not while loading the module
    """
    aws = None
    do = None

    def __init__(self, ACCESS_KEY, SECRET, REGION):
        self.ACCESS_KEY = ACCESS_KEY
        self.SECRET = SECRET
        self.REGION = REGION

    def make_aws_conn(self):
        AWS_BASE_URL = 'https://s3.amazonaws.com'
        return boto3.resource('s3',
                              region_name=self.REGION,
                              endpoint_url=AWS_BASE_URL,
                              aws_access_key_id=self.ACCESS_KEY,
                              aws_secret_access_key=self.SECRET)

    def make_do_conn(self):
        DO_BASE_URL = 'https://%s.%s' % (self.REGION, 'digitaloceanspaces.com')
        return boto3.resource('s3',
                              region_name=self.REGION,
                              endpoint_url=DO_BASE_URL,
                              aws_access_key_id=self.ACCESS_KEY,
                              aws_secret_access_key=self.SECRET)

    def __getitem__(self, name):
        conn = None
        if name == 'amazon':
            if self.aws is None:
                self.aws = self.make_aws_conn()
            conn = self.aws
        elif name == 'digitalocean':
            if self.do is None:
                self.do = self.make_do_conn()
            conn = self.do
        return conn

    def upload_file_to_cloud(self, service, bucket, logger,
                             media_location, file_key, DELETE_DUMP):
        """
        Uploads file to Cloud (Amazon or DigitalOcean) S3 services
        Arguments:
            media_location -- File location in local storage
            file_key -- file key, the directory path where the file is stored
            service -- 'amazon' for Amazon or 'digitalocean'
            bucket -- bucket name
        """
        logger.info('Uploading file key {} to Cloud ...'.format(file_key))
        buck = self.__getitem__(service).Bucket(bucket)
        buck.put_object(
            Key=file_key,
            Body=open(media_location, 'rb'),
            ACL='public-read')
        logger.info('Uploaded file key {}.'.format(file_key))
        if DELETE_DUMP:
            os.remove(media_location)
            logger.info('''Removed the dump from
                        local directory ({}).'''.format(media_location))
