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
import tempfile

logger = logging.getLogger('s3_dumps')


def create_db_dump(command, filename):
    """
    Creates dump file using pg_dump
    Returns:
        1: Path of dump file from temp storage
    """
    if DUMP_BASE_DIR and not os.path.exists(DUMP_BASE_DIR):
        os.mkdir(DUMP_BASE_DIR)

    logger.info("Preparing " + filename + ".sql from the database dump ...")
    with tempfile.NamedTemporaryFile() as temp1:
        ps = subprocess.Popen(
            command,
            stdout=temp1, shell=True, universal_newlines=True
        )
        ps.wait()
        temp1.flush()

        tar = tarfile.open(DUMP_BASE_DIR + filename + ".tar.gz", "w|gz")
        tar.add(temp1.name, filename + ".sql")
        tar.close()
    logger.info("Created tar file " + filename + ".tar.gz")
    return '{}{}.tar.gz'.format(DUMP_BASE_DIR, filename)


def backup():
    """Creates the buckup and uploads"""
    now = datetime.now()
    archive_name = DB_NAME + '_db' if DB_NAME else ARCHIVE_NAME
    filename = archive_name + now.strftime('_%Y%m%d_%H%M%S')
    if DB_NAME:
        command = [
            POSTGRES_DUMP_CMD,
            '-Fc', DB_NAME,
            '-f', DUMP_BASE_DIR + filename + ".sql"
        ]
    else:
        command = [
            POSTGRES_DUMP_CMD + 'all',
            '-f', DUMP_BASE_DIR + filename + ".sql"
        ]

    file_location = create_db_dump(command, filename)
    file_key_suffix = utils.get_file_key(file_key=FILE_KEY, db_name=DB_NAME)
    file_key = r'%s/%s' % (file_key_suffix, filename + '.tar.gz')

    conn.upload_file_to_cloud(
        bucket=BUCKET_NAME,
        media_location=file_location,
        file_key=file_key
    )

    if DELETE_DUMP:
        os.remove(file_location)
        logger.info('''Removed the dump from local directory ({}).'''.format(
            file_location))

    logger.info('Sucessfully uploaded the Dump.')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='''Creates postgres DB
                                     dump and stores it to S3 using
                                     `pg_dump`.''')
    parser = utils.init_arguments(parser)

    parser.add_argument('--ARCHIVE_NAME',
                        default='all_postgres_db',
                        help='The base name for the archive')

    parser.add_argument('--POSTGRES_DUMP_CMD',
                        default='pg_dump',
                        help='''Path to pg_dumpall (default: pg_dump).
                        You may change according to system
                        Eg. /usr/bin/pg_dump''')

    args = parser.parse_args()

    SERVICE_NAME = args.SERVICE_NAME
    ACCESS_KEY = args.ACCESS_KEY
    SECRET = args.SECRET
    REGION = args.REGION
    BUCKET_NAME = args.BUCKET_NAME
    FILE_KEY = args.FILE_KEY

    DB_NAME = args.DB_NAME
    DELETE_DUMP = args.DELETE_DUMP
    DUMP_BASE_DIR = args.DUMP_BASE_DIR
    ARCHIVE_NAME = args.ARCHIVE_NAME

    POSTGRES_DUMP_CMD = args.POSTGRES_DUMP_CMD
    conn = s3Connect(access_key_id=ACCESS_KEY, secret_access_key=SECRET, region=REGION, service_name=SERVICE_NAME)

    if args.verbose:
        utils.init_logger(logger)

    if args.archive:
        archive = Archive(conn=conn.get_conn(), service_name=SERVICE_NAME,
                          bucket=BUCKET_NAME, file_key=FILE_KEY, db_name=DB_NAME)
        archive.archive()

    if args.backup:
        backup()
