.PHONY: db-up db-down db-reset tts-build tts-up stack-up stack-down

db-up:
	docker compose up --detach --wait postgres

db-down:
	docker compose down

# Deletes the database volume, then starts an empty database with its tables
db-reset:
	docker compose down --volumes
	$(MAKE) db-up
	poetry run poe db-create

tts-build:
	docker compose build tts

# Starts the speech service on localhost:TTS_PORT, so `poe api` can reach it
tts-up:
	docker compose up --build --detach --wait tts

stack-up:
	docker compose up --build

stack-down:
	docker compose down
