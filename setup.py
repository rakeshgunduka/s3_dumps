from setuptools import setup

setup(
    name='s3_dumps',
    packages=['s3_dumps'],
    version=__import__('s3_dumps').__version__,
    description='A package for backup DB and store in s3',
    author='Reck31',
    author_email='rakesh.gunduka@gmail.com',
    url='https://github.com/rakeshgunduka/s3_dumps',
    include_package_data=True,
    install_requires=[
        "boto3"
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only'
    ],
    entry_points={
        'console_scripts': [
            'postgres_to_s3=s3_dumps.postgres_to_s3:main',
            'redis_to_s3=s3_dumps.redis_to_s3:main'
        ],
    },
    scripts=[
        's3_dumps/postgres_to_s3.py',
        's3_dumps/redis_to_s3.py'
    ],
    keywords = ['s3', 'backup', 'postgres', 'redis', 'digitaloceanspaces', 'aws'],
    zip_safe=False
)
