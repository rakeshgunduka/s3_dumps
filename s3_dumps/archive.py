from datetime import datetime

import re


class Archive(object):
    """
    Archives all backups on S3 using the following schedule:

    - Keep all backups for 7 days
    - Keep midnight backups for every other day for 30 days
    - Keep 1st day of the month forever
    """

    def __init__(self, conn, SERVICE_NAME, BUCKET_NAME, FILE_KEY):
        self.conn = conn
        self.SERVICE_NAME = SERVICE_NAME
        self.BUCKET_NAME = BUCKET_NAME
        self.FILE_KEY = FILE_KEY

    def schedule(self, conn, schedule_module='schedule'):
        schedule = __import__(schedule_module)
        bucket = self.conn[self.SERVICE_NAME].get_bucket(self.BUCKET_NAME)

        file_key = self.FILE_KEY if self.FILE_KEY.endswith('/') else self.FILE_KEY + '/'

        for obj in bucket.objects.filter(Prefix=file_key):
            if not obj.key.endswith("/"):

                obj = self.add_datetimes_to_key(obj)

                # create a new key that puts the archive in a year/mon`th sub
                # directory if it's not in a year/month sub directory already
                name_parts = obj.key.split('/')
                month = name_parts[-2]
                year = name_parts[-3]
                new_key_name = obj.key
                if not re.match(r'[\d]{4}', year) and not re.match(r'[\d]{2}', month):
                    name_parts.insert(len(name_parts) - 1, "%d" % obj.local_last_modified.year)
                    name_parts.insert(len(name_parts) - 1, "%02d" % obj.local_last_modified.month)
                    new_key_name = "/".join(name_parts)

                # either keep the file or delete it
                keep_file = schedule.keep_file(obj)
                if keep_file and obj.key != new_key_name:
                    self.conn.Object(self.BUCKET_NAME, new_key_name, metadata=key.meta, preserve_acl=True).copy_from(CopySource=obj.key)
                    bucket.delete_key(obj.key)
                elif not keep_file:
                    bucket.delete_key(obj.key)

    def add_datetimes_to_key(self, obj):
        """
        Convert the last_modified GMT datetime string to a datetime object and
        create utc and local datetime objects.
        """

        utc = tz.tzutc()
        gmt = tz.gettz('GMT')
        local_tz = tz.tzlocal()

        obj.last_modified = datetime.strptime(obj.last_modified, "%Y-%m-%dT%H:%M:%S.%fZ")
        obj.last_modified = obj.last_modified.replace(tzinfo=gmt)
        obj.utc_last_modified = obj.last_modified.astimezone(utc)
        obj.local_last_modified = obj.last_modified.astimezone(local_tz)

        return obj
