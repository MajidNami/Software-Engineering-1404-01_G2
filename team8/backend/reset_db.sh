#!/bin/bash
set -e

DB_NAME="backend_db"
DB_USER="backend_user"
DB_PASS="backend_pass"
DB_HOST="localhost"
DB_PORT="5433"

echo "Resetting database..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# echo "Running schema migration..."
# PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f db/migrations/001_initial_schema.sql

# echo "Seeding reference data..."
# PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f db/migrations/002_seed_reference_data.sql

echo "Done!"
