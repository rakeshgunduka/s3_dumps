#!/usr/bin/env python

from datetime import datetime
from s3_dumps.connect import s3Connect
from s3_dumps.archive import Archive

import os
import sys
import argparse

import s3_dumps.utils as utils

import logging
import tarfile

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
    logger.info('Preparing ' + filename + '.sql from the database dump ...')
    logger.info('Executing: %s', command)
    ret = os.system(command)
    if ret != 0:
        sys.exit(ret)
    tar = tarfile.open(DUMP_BASE_DIR + filename + '.tar.gz', 'w|gz')
    tar.add(DUMP_BASE_DIR + filename + '.sql', filename + '.sql')
    tar.close()
    logger.info('Created tar file ' + filename + '.tar.gz')
    return '{}{}.tar.gz'.format(DUMP_BASE_DIR, filename)


def backup():
    """Creates the buckup and uploads"""
    now = datetime.now()
    archive_name = DB_NAME + '_db' if DB_NAME else ARCHIVE_NAME
    filename = archive_name + now.strftime('_%Y%m%d_%H%M%S')

    command = '{0} -h {1} -u {2} -p {3}'.format(MYSQL_DUMP_CMD, MYSQL_HOST,
                                                MYSQL_USER, MYSQL_PASSWORD)
    if DB_NAME:
        command += ' --databases {4} > {5}'.format(DB_NAME, DUMP_BASE_DIR + filename + '.sql')
    else:
        command += ' --all-databases > {5}'.format(DUMP_BASE_DIR + filename + '.sql')

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
                        default='all_mysql_db',
                        help='The base name for the archive')
    parser.add_argument('--MYSQL_DUMP_CMD',
                        default='mysqldump',
                        help="mysqldump command (default: mysqldump)")
    parser.add_argument('--MYSQL_HOST',
                        default='localhost',
                        help="Mysql host (default: localhost)")
    parser.add_argument('--MYSQL_USER',
                        default='root', help="Mysql user (default: root)")
    parser.add_argument('--MYSQL_PASSWORD',
                        default='', help="Mysql password (default: '')")

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

    MYSQL_DUMP_CMD = args.MYSQL_DUMP_CMD
    MYSQL_HOST = args.MYSQL_HOST
    MYSQL_USER = args.MYSQL_USER
    MYSQL_PASSWORD = args.MYSQL_USER

    conn = s3Connect(access_key_id=ACCESS_KEY, secret_access_key=SECRET, region=REGION, service_name=SERVICE_NAME)

    if args.verbose:
        utils.init_logger(logger)

    if args.archive:
        archive = Archive(conn=conn.get_conn(), service_name=SERVICE_NAME,
                          bucket=BUCKET_NAME, file_key=FILE_KEY, db_name=DB_NAME)
        archive.archive()

    if args.backup:
        backup()
