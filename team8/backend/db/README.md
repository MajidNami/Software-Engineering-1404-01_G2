# Team 8 Database Migrations

This directory contains SQL migration files for the Team 8 database schema.

## Running Migrations

### Development (Local)
```bash
# Connect to your local PostgreSQL
psql -U team8_user -d team8_db -f migrations/001_initial_schema.sql
```

### Production (Cloud MySQL - after TA approval)
The TA team will apply these migrations to the cloud database after review.

## Migration Files

- `001_initial_schema.sql` - Initial database schema for Team 8

## Notes

- All tables use `team8_` prefix to avoid conflicts
- User references (user_id) link to core.users table
- Indexes are created for performance
- Soft deletes used for media and comments (deleted_at column)
