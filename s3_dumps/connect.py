import boto3
import logging

logger = logging.getLogger('s3_dumps')


class s3Connect:
    """
    Connect to s3 using credentials
    Arguments:
        access_key_id -- Access Key ID
        secret_access_key -- Secret Acces Key
        region -- bucket region (default is set to '')
        service_name -- default is set to amazon (supported services - digitalocean and amazon)
    """

    def __init__(self, access_key_id, secret_access_key, region='', service_name='amazon'):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region = region
        self.service_name = service_name

        if service_name == 'amazon':
            aws_base_url = 'https://s3.amazonaws.com'
            self.conn = boto3.resource('s3',
                                  region_name=region,
                                  endpoint_url=aws_base_url,
                                  aws_access_key_id=access_key_id,
                                  aws_secret_access_key=secret_access_key)
        elif self.service_name == 'digitalocean':
            do_base_url = 'https://%s.%s' % (region, 'digitaloceanspaces.com')
            self.conn = boto3.resource('s3',
                                  region_name=region,
                                  endpoint_url=do_base_url,
                                  aws_access_key_id=access_key_id,
                                  aws_secret_access_key=secret_access_key)
        else:
            raise Exception('Unsupported service name: %s', self.service_name)

    def get_conn(self):
        return self.conn

    def upload_file_to_cloud(self, bucket, media_location, file_key):
        """
        Uploads file to Cloud (Amazon or DigitalOcean) S3 services
        Arguments:
            media_location -- File location in local storage
            file_key -- file key, the directory path where the file is stored
            service -- 'amazon' for Amazon or 'digitalocean'
            bucket -- bucket name
        """
        logger.info('Uploading file key {} to Cloud ...'.format(file_key))
        buck = self.conn.Bucket(bucket)
        try:
            buck.put_object(
                Key=file_key,
                Body=open(media_location, 'rb'),
                ACL='public-read')
            logger.info('Uploaded file key {}.'.format(file_key))
        except Exception as e:
            logger.info('Error: ', e)
