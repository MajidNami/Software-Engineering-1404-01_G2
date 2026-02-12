# Database Migrations with Alembic

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema migrations, following FastAPI best practices.

## Setup

Alembic is already configured and initialized. The configuration files are:
- `alembic.ini` - Main Alembic configuration
- `alembic/env.py` - Migration environment setup
- `alembic/versions/` - Migration scripts directory

## Environment Variables

Set the database URL before running any Alembic commands:
```bash
export AI_DATABASE_URL="postgresql://ai_user:ai_pass@localhost:5434/ai_db"
```

Or use the `.env.local` file (automatically loaded by the application).

## Common Commands

### Apply migrations (upgrade database)
```bash
alembic upgrade head
```

### Create a new migration (after modifying models.py)
```bash
# Autogenerate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration in alembic/versions/
# Then apply it:
alembic upgrade head
```

### Check current migration version
```bash
alembic current
```

### View migration history
```bash
alembic history
```

### Rollback to previous version
```bash
alembic downgrade -1
```

### Rollback to specific version
```bash
alembic downgrade <revision_id>
```

## Workflow for Schema Changes

1. **Modify your SQLAlchemy models** in `models.py`
2. **Generate migration**: `alembic revision --autogenerate -m "Add new column"`
3. **Review the generated migration** in `alembic/versions/`
4. **Apply migration**: `alembic upgrade head`
5. **Commit** both the model changes and the migration file to git

## Initial Schema

The initial schema includes:
- `text_moderation` - Post content moderation results
- `image_moderation` - Image NSFW detection results
- `image_tagging` - Image place/landmark detection
- `place_summaries` - AI-generated place summaries from reviews
- `analysis_status` enum type (PENDING, PROCESSING, COMPLETED, FAILED)

## Migration Files

Migration files are located in `alembic/versions/` and are automatically named with:
- Revision ID (e.g., `ec3ff9d1ef7d`)
- Description slug
- Timestamp

## Notes

- Never manually edit the database schema directly
- Always use Alembic for schema changes
- Keep migration files in version control
- Test migrations on development database before production
- Alembic tracks applied migrations in the `alembic_version` table
