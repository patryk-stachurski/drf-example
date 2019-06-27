#!/bin/bash

set -e
set -u

echo "Setting up the database..."

source /docker-entrypoint-initdb.d/.env

export PGUSER=postgres

RUN_PSQL="psql -X --set AUTOCOMMIT=off --set ON_ERROR_STOP=on "


${RUN_PSQL} <<SQL
CREATE DATABASE ${DB_NAME};


CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';

ALTER ROLE ${DB_USER} SET client_encoding TO 'utf8';
ALTER ROLE ${DB_USER} SET default_transaction_isolation TO 'read committed';
ALTER ROLE ${DB_USER} SET timezone TO 'UTC';

ALTER USER ${DB_USER} CREATEDB;


GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};

COMMIT;
SQL

sed -i -e"s/^#port = 5432.*$/port = ${DB_PORT}/" /var/lib/postgresql/data/postgresql.conf
sed -i -e"s/^host    all             all             127.0.0.1\\/32            trust.*$/host    all             all             0.0.0.0\\/32            trust/" /var/lib/postgresql/data/pg_hba.conf


echo "Setup of the database completed successfully!"
