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

check.uncompressed_size:
	@if [ "$(path)" == "" ]; then \
		echo -e "Missing 'path' argument as the Zip/7z ROMs directory path"; \
		exit 1; \
	fi;
	python scripts/check_compressed_file_size.py $(path)

copy_extract.zip_roms:
	@if [ "$(path)" == "" ]; then \
		echo -e "Missing 'path' argument as the ZIP ROMs directory path"; \
		exit 1; \
	fi;
	@if [ "$(outdir)" == "" ]; then \
		echo -e "Missing 'outdir' argument as the output directory path"; \
		exit 1; \
	fi;
	python scripts/copy_extract_zip_roms.py $(path) $(outdir)
