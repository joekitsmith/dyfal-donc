.PHONY: db-up db-down db-reset stack-up stack-down

db-up:
	docker compose up --detach --wait postgres

db-down:
	docker compose down

# Deletes the database volume, then starts an empty database with its tables
db-reset:
	docker compose down --volumes
	$(MAKE) db-up
	poetry run poe db-create

stack-up:
	docker compose up --build

stack-down:
	docker compose down
