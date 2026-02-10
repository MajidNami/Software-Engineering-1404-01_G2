#!/bin/bash
set -e

DB_NAME="team8_db"
DB_USER="team8_user"
DB_PASS="team8_pass"
DB_HOST="localhost"

echo "Resetting database..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo "Running schema migration..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f db/migrations/001_initial_schema.sql

echo "Seeding reference data..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f db/migrations/002_seed_reference_data.sql

echo "Done!"
