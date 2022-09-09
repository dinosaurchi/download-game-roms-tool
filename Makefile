SHELL := /bin/bash

download.all: output_dir="/hdd2/game-roms"
download.all: account="secrets/archive.org.json"
download.all:
	@if [ "$(db)" == "" ]; then \
		echo -e "Missing 'db' argument as the file path to the game database"; \
		exit 1; \
	fi;
	@python ./run.py \
		--database $(db) \
		--out $(output_dir) \
		--account $(account)

check.uncompressed_zip:
	@if [ "$(path)" == "" ]; then \
		echo -e "Missing 'path' argument as the ZIP ROMs directory path"; \
		exit 1; \
	fi;
	python scripts/check_zip_file_size.py $(path)