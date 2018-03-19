from datetime import datetime, timedelta
from dateutil import tz

import s3_dumps.utils as utils

import os
import re
import logging

logger = logging.getLogger('s3_dumps')


class Archive(object):
    """
    Archives all backups on S3 using the following schedule:

    - Keep all backups for 7 days
    - Keep midnight backups for every other day for 30 days
    - Keep 1st day of the month forever
    """

    def __init__(self, conn, service_name, bucket, file_key, db_name=None):
        self.conn = conn
        self.service_name = service_name
        self.bucket = bucket
        self.file_key_suffix = utils.get_file_key(file_key=file_key, db_name=db_name)

    def archive(self):
        buck = self.conn.Bucket(self.bucket)
        for obj in buck.objects.filter(Prefix=self.file_key_suffix):
            if not obj.key.endswith("/"):
                name_parts = obj.key.split('/')
                month = name_parts[-2]
                year = name_parts[-3]
                new_key_name = obj.key

                if not re.match(r'[\d]{4}', year) and not re.match(r'[\d]{2}', month):
                    path, filename = os.path.split(obj.key)
                    new_key_name = '{path}/{year}/{month}/{day}/{filename}'.format(
                            path=path,
                            year=obj.last_modified.year,
                            month=obj.last_modified.month,
                            day=obj.last_modified.day,
                            filename=filename
                        )

                if self.remove_key(obj):
                    obj.delete()
                elif obj.key != new_key_name:
                    logger.info('Archiving object to {new_key}'.format(
                        key=obj.key,
                        new_key=new_key_name,
                    ))
                    copy_source = {'Bucket': obj.bucket_name, 'Key': obj.key}
                    new_obj = self.conn.Object(self.bucket, new_key_name)
                    new_obj.copy_from(CopySource=copy_source)
                    obj.delete()

    def remove_key(self, obj):
        delta = datetime.now().astimezone(tz=tz.tzutc()) - obj.last_modified
        week_delta = timedelta(days=7)
        month_delta = timedelta(days=30)

        if delta <= week_delta:
            logger.info('%s - Keeping object \"%s\" because it\'s less than a week old.' % (delta, obj.key))
            return False
        elif week_delta < delta < month_delta:
            if obj.last_modified.hour != 0:
                logger.info('%s - Removing object \"%s\" because it\'s not a midnight backup and it\'s older than one week but less than a month' % (delta, obj.key))
                return True
            elif obj.last_modified.day % 2 != 0:
                logger.info('%s - Removing object \"%s\" because it\'s older than one week but less than a month and not an even day.' % (delta, obj.key))
                return True
            else:
                logger.info('%s - Keeping object \"%s\" because it\'s older than one week but less than a month and it\'s an even day.' % (delta, obj.key))
                return False
        elif delta > month_delta:
            if obj.month_delta.day == 1:
                logger.info('%s - Keeping object \"%s\" because it\'s older than a month and also the first day of the month.' % (delta, obj.key))
                return False
            else:
                logger.info('%s - Removing object \"%s\" because it\'s older than a month and not the first day of the month.' % (delta, obj.key))
                return True
