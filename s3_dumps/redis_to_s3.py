#!/usr/bin/env python

from datetime import datetime
from s3_dumps.connect import s3Connect
from s3_dumps.archive import Archive

import os
import argparse
import subprocess

import s3_dumps.utils as utils

import logging
import tarfile

logger = logging.getLogger('s3_dumps')


def create_redis_dump(filename):
    """
    Creates dump file using pg_dump
    Returns:
        1: Path of dump file from temp storage
    """
    if DUMP_BASE_DIR and not os.path.exists(DUMP_BASE_DIR):
        os.mkdir(DUMP_BASE_DIR)

    logger.info("Preparing " + filename + ".rdb from the database dump ...")
    logger.info(REDIS_SAVE_CMD)
    ps = subprocess.Popen(
            REDIS_SAVE_CMD, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    ps.wait()

    redis_dump_dir = REDIS_DUMP_DIR if REDIS_DUMP_DIR.endswith('/') else REDIS_DUMP_DIR + '/'

    tar = tarfile.open(DUMP_BASE_DIR + filename + ".tar.gz", "w|gz")
    tar.add(redis_dump_dir + 'dump.rdb', filename + ".rdb")
    tar.close()
    logger.info("Created tar file " + filename + ".tar.gz")

    return '{}{}.tar.gz'.format(DUMP_BASE_DIR, filename)


def backup():
    """Creates the buckup and uploads"""
    now = datetime.now()
    filename = ARCHIVE_NAME + now.strftime('_%Y%m%d_%H%M%S')

    file_location = create_redis_dump(filename)
    file_key_suffix = utils.get_file_key(file_key=FILE_KEY)
    file_key = r'%s/%s' % (file_key_suffix, filename + '.tar.gz')

    conn.upload_file_to_cloud(
        bucket=BUCKET_NAME,
        media_location=file_location,
        file_key=file_key
    )
    
    logger.info('Sucessfully uploaded the Dump.')



if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                description='''Creates redis DB dump and stores
                it to S3 using `redis-cli save`.''')
    parser = utils.init_arguments(parser)
    parser.add_argument('--ARCHIVE_NAME',
                        default='all_redis_db',
                        help='The base name for the archive')

    args = parser.parse_args()

    SERVICE_NAME = args.SERVICE_NAME
    ACCESS_KEY = args.ACCESS_KEY
    SECRET = args.SECRET
    REGION = args.REGION
    BUCKET_NAME = args.BUCKET_NAME
    FILE_KEY = args.FILE_KEY

    DUMP_BASE_DIR = args.DUMP_BASE_DIR

    REDIS_DUMP_DIR = args.REDIS_DUMP_DIR
    REDIS_SAVE_CMD = args.REDIS_SAVE_CMD
    ARCHIVE_NAME = args.ARCHIVE_NAME

    conn = s3Connect(access_key_id=ACCESS_KEY, secret_access_key=SECRET, region=REGION, service_name=SERVICE_NAME)

    if args.verbose:
        utils.init_logger(logger)

    if args.archive:
        archive = Archive(
                    conn=conn.get_conn(), service_name=SERVICE_NAME,
                    bucket=BUCKET_NAME, file_key=FILE_KEY)
        archive.archive()

    if args.backup:
        backup()
