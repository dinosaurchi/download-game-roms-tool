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
