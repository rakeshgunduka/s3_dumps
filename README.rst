S3 Dumps
==========

|Build Status|

Note: A rewritten fork of `s3-backups` <https://github.com/epicserve/s3-backups>.

`S3 Dumps <https://github.com/epicserve/s3-backups>`_ provides easy scripts that system administrators can use to backup
data from programs likes PostgreSQL, Redis, etc.

.. |Build Status| raw:: html

    <a href="https://travis-ci.org/rakeshgunduka/s3_dumps">
        <img src="https://travis-ci.org/rakeshgunduka/s3_dumps.png?branch=master"/>
    </a>

Installation
------------

To install s3-backups::

    $ sudo pip install s3_dumps

Usage
-----

For Backup
''''''''''
Using --backup flag, the script creates the dump and stores in the bucket as it is without year/month/date directory structure.

::

    --backup

For Archive
'''''''''''
Using --archive flag, the script takes all the files from the bucket and archives it in year/month/date directory structure.

::

    --archive

For Archive and Backup
''''''''''''''''''''''
Using --backup --archive flags together, the script takes all the files from the bucket and archives it in year/month/date directory structure and creates a dump at the parent directory (inside Bucket).

::

    --backup --archive
    
To dump into amazon s3 service.
'''''''''''''''''''''''''''''''
Set --SERVICE_NAME to 'amazon'.

::

    --SERVICE_NAME='amazon'

To dump into digitalocean spaces.
'''''''''''''''''''''''''''''''''
Set --SERVICE_NAME to 'digitalocean'.

::

    --SERVICE_NAME='digitalocean'


Setting Up S3 Dumps to Run Automatically Using Cron
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PostgreSQL
''''''''''

Add the following to the file ``/etc/cron.d/postgres_to_s3`` and then change the command arguments so the command is using your correct AWS credentials, backup bucket and the correct base S3 Key/base folder.


Amazon Services
::

    0 */1 * * * postgres postgres_to_s3.py --SERVER_NAME='amazon' --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' --SECRET='xxxxxxxxxxxxxxxxxxxx' --REGION='bucket-region' --BUCKET_NAME='my-backup-bucket' --FILE_KEY='postgres/my-awesome-server' --backup

Digitalocen Spaces
::

    0 */1 * * * postgres postgres_to_s3.py --SERVER_NAME='digitalocean' --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' --SECRET='xxxxxxxxxxxxxxxxxxxx' --REGION='bucket-region' --BUCKET_NAME='my-backup-bucket' --FILE_KEY='postgres/my-awesome-server' --backup

To create dump of a specific database (my-db-name).
::

    0 */1 * * * postgres postgres_to_s3.py --SERVER_NAME='amazon' --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' --SECRET='xxxxxxxxxxxxxxxxxxxx' --REGION='bucket-region' --BUCKET_NAME='my-backup-bucket' --DB_NAME='my-db-name' --FILE_KEY='postgres/my-awesome-server' --backup

To backup and archive at the same time.
::

     0 */1 * * * postgres postgres_to_s3.py --SERVER_NAME='amazon' --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' --SECRET='xxxxxxxxxxxxxxxxxxxx' --REGION='bucket-region' --BUCKET_NAME='my-backup-bucket' --FILE_KEY='postgres/my-awesome-server' --backup --archive


Redis
'''''

Add the following to the file ``/etc/cron.d/redis_to_s3`` and then change the command arguments so the command is using your correct AWS credentials, backup bucket and the correct base S3 Key/base folder.

Amazon Services
::

    0 */1 * * * postgres redis_to_s3.py --SERVER_NAME='amazon' --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' --SECRET='xxxxxxxxxxxxxxxxxxxx' --REGION='bucket-region' --BUCKET_NAME='my-backup-bucket' --FILE_KEY='postgres/my-awesome-server' --backup

Digitalocen Spaces
::

    0 */1 * * * postgres redis_to_s3.py --SERVER_NAME='digitalocean' --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' --SECRET='xxxxxxxxxxxxxxxxxxxx' --REGION='bucket-region' --BUCKET_NAME='my-backup-bucket' --FILE_KEY='postgres/my-awesome-server' --backup

Provide Redis working according to the system redis config directory. (Not mandatory field) If not provided it sets to default.
::

    0 */1 * * * root redis_to_s3.py --SERVER_NAME='amazon' --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' --SECRET='xxxxxxxxxxxxxxxxxxxx' --REGION='bucket-region' --BUCKET_NAME='my-backup-bucket' --FILE_KEY='redis/my-awesome-server' --REDIS_DUMP_DIR='/Your/Redis/Config/Dir' --backup

To backup and archive at the same time.
::

     0 */1 * * * root redis_to_s3.py --SERVER_NAME='amazon' --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' --SECRET='xxxxxxxxxxxxxxxxxxxx' --REGION='bucket-region' --BUCKET_NAME='my-backup-bucket' --FILE_KEY='redis/my-awesome-server' --REDIS_DUMP_DIR='/Your/Redis/Config/Dir' --REDIS_SAVE_CMD='redis-cli save' --backup --archive

Manually Running Dumps and Archiving
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When running the archive command, S3 Dumps moves backups into a
``year/month/date`` sub folder (technically a S3 key).

The default archive mode will ...

- keep all archives for 7 days
- keep midnight backups for every other day for 30 days
- keep the first day of the month forever
- remove all other files that aren't scheduled to be kept

To backup PostgreSQL, run the following::

    $ postgres_to_s3.py \
    --SERVER_NAME='amazon'
    --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' \
    --SECRET='xxxxxxxxxxxxxxxxxxxx' \
    --REGION='bucket-region' \
    --BUCKET_NAME='my-backup-bucket' \
    --FILE_KEY='postgres/my-awesome-server' \
    --backup

To archive PostgreSQL backups, run the following::

    $ postgres_to_s3.py \
    --SERVER_NAME='amazon'
    --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' \
    --SECRET='xxxxxxxxxxxxxxxxxxxx' \
    --REGION='bucket-region' \
    --BUCKET_NAME='my-backup-bucket' \
    --FILE_KEY='postgres/my-awesome-server' \
    --archive

To backup Redis, run the following::

    $ redis_to_s3.py \
    --SERVER_NAME='amazon'
    --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' \
    --SECRET='xxxxxxxxxxxxxxxxxxxx' \
    --REGION='bucket-region' \
    --BUCKET_NAME='my-backup-bucket' \
    --FILE_KEY='postgres/my-awesome-server' \
    --REDIS_DUMP_DIR='/Your/Redis/Config/Dir' \
    --REDIS_SAVE_CMD='redis-cli save' \
    --backup


To archive Redis, run the following::

    $ redis_to_s3.py \
    --SERVER_NAME='amazon'
    --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' \
    --SECRET='xxxxxxxxxxxxxxxxxxxx' \
    --REGION='bucket-region' \
    --BUCKET_NAME='my-backup-bucket' \
    --FILE_KEY='postgres/my-awesome-server' \
    --REDIS_DUMP_DIR='/Your/Redis/Config/Dir' \
    --REDIS_SAVE_CMD='redis-cli save' \
    --archive

To backup MySQL, run the following::

    $ mysql_to_s3.py \
    --SERVER_NAME='amazon'
    --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' \
    --SECRET='xxxxxxxxxxxxxxxxxxxx' \
    --REGION='bucket-region' \
    --BUCKET_NAME='my-backup-bucket' \
    --FILE_KEY='postgres/my-awesome-server' \
    --backup

To archive MySQL, run the following::

    $ mysql_to_s3.py \
    --SERVER_NAME='amazon'
    --ACCESS_KEY='xxxxxxxxxxxxxxxxxxxx' \
    --SECRET='xxxxxxxxxxxxxxxxxxxx' \
    --REGION='bucket-region' \
    --BUCKET_NAME='my-backup-bucket' \
    --FILE_KEY='postgres/my-awesome-server' \
    --backup

To Do's
----------

1.  Add tests

Contributers
----------

1.  `Brent O\'Connor <https://github.com/epicserve>`_
2.  `Rakesh Gunduka <https://github.com/rakeshgunduka>`_
3.  `Shekhar Tiwatne <https://github.com/shon>`_
