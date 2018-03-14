#!/usr/bin/env python

from datetime import datetime
from connect import s3Connect

import os
import argparse
import subprocess

import utils

import logging
import tarfile

logger = logging.getLogger('s3_backups')


def create_redis_dump(filename):
    """
    Creates dump file using pg_dump
    Returns:
        1: Path of dump file from temp storage
    """
    if not os.path.exists(DUMP_BASE_DIR):
        os.mkdir(DUMP_BASE_DIR)

    logger.info("Preparing " + filename + ".dump from the database dump ...")
    ps = subprocess.Popen(
            REDIS_SAVE_CMD, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    ps.wait()

    tar = tarfile.open(DUMP_BASE_DIR + filename + ".tar.gz", "w|gz")
    tar.add(DUMP_RDB_PATH, filename + ".rdb")
    tar.close()
    logger.info("Created tar file " + filename + ".tar.gz")
    return '{}{}.tar.gz'.format(DUMP_BASE_DIR, filename)


def backup():
    """Creates the buckup and uploads"""
    now = datetime.now()
    filename = ARCHIVE_NAME + now.strftime('_%Y%m%d_%H%M%S')

    file_location = create_redis_dump(filename)
    file_key = utils.get_file_key(FILE_KEY, filename, ARCHIVE)

    conn.upload_file_to_cloud(
        media_location=file_location,
        file_key=file_key,
        service=SERVICE_NAME,
        bucket=BUCKET_NAME
    )

    if DELETE_DUMP:
        os.removedirs(DUMP_BASE_DIR)

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

    DELETE_DUMP = args.DELETE_DUMP
    DUMP_BASE_DIR = args.DUMP_BASE_DIR

    DUMP_RDB_PATH = args.DUMP_RDB_PATH
    REDIS_SAVE_CMD = args.REDIS_SAVE_CMD
    ARCHIVE_NAME = args.ARCHIVE_NAME

    conn = s3Connect(ACCESS_KEY, SECRET, REGION)

    if args.archive:
        ARCHIVE = True

    if args.verbose:
        utils.init_logger()

    if args.backup or args.archive:
        backup()
