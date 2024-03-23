SHELL := /bin/bash

build:
	@docker build  -t charlesdajing/tiktokapi:latest .

run:
	docker run -it --rm -v $(shell pwd):/app -e HEADLESS=False --net=host charlesdajing/tiktokapi:latest
