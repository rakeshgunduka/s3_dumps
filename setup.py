from setuptools import setup

setup(
    name='s3_dumps',
    version=__import__('s3_dumps').__version__,
    description='A package for backup DB and store in s3',
    author='Reck31',
    author_email='rakesh.gunduka@gmail.com',
    include_package_data=True,
    license=open('LICENSE').read(),
    packages=['s3_dumps'],
    install_requires=[
        "boto3"
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    entry_points = {
        'console_scripts': [
            'postgres_dump=s3_dumps.postgres_dump:main',
            'redis_dump=s3_dumps.redis_dump:main'
        ],
    },
    scripts = ['s3_dumps/postgres_dump.py', 's3_dumps/redis_dump.py', 's3_dumps/connect.py', 's3_dumps/utils.py'],
    zip_safe=False
)