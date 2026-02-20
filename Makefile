.PHONY: up down build shell

down:
	docker compose down

build:
	docker compose build

up:
	docker compose run --rm --service-ports pdsim-server
