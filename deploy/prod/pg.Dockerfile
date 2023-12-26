FROM ankane/pgvector:latest



ADD db_dump.sql /docker-entrypoint-initdb.d/
