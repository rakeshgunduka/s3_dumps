help:
	-@ echo "clean          remove build dirs"
	-@ echo "lint           check the code using pep8 and pyflakes"

clean:
	-@ rm -rf build/
	-@ rm -rf dist/
	-@ rm -rf s3_dumps.egg-info/

lint:
	@echo "Checking code using pep8 and pyflakes ..."
	@flake8 s3_dumps


backup_postgres:
	-s3_backups/postgres_to_s3.py \
		-v \
		--SERVICE_NAME=$(SERVICE_NAME) \
		--ACCESS_KEY=$(ACCESS_KEY) \
		--SECRET=$(SECRET) \
		--REGION=$(REGION) \
		--BUCKET_NAME=$(BUCKET_NAME) \
		--FILE_KEY=$(FILE_KEY) \
		--POSTGRES_DUMP_CMD=$(POSTGRES_DUMP_CMD) \
		--DB_NAME=$(DB_NAME) \
		--backup

archive_postgres:
	-s3_backups/postgres_to_s3.py \
		-v \
		--SERVICE_NAME=$(SERVICE_NAME) \
		--ACCESS_KEY=$(ACCESS_KEY) \
		--SECRET=$(SECRET) \
		--REGION=$(REGION) \
		--BUCKET_NAME=$(BUCKET_NAME) \
		--FILE_KEY=$(FILE_KEY) \
		--POSTGRES_DUMP_CMD=$(POSTGRES_DUMP_CMD) \
		--DB_NAME=$(DB_NAME) \
		--archive