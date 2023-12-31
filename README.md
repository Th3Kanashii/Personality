# Personality

Personality is a Telegram bot created to provide support and useful
knowledge aimed at your personal development and adaptation in the modern
society.
There are four key areas, and by choosing each of them, you will discover
the opportunity to receive information and ask questions
to our qualified volunteer experts.

# Deployment

## Via Docker
1. Rename `.env.dist` to `.env` and configure it
2. Run `make app-build` command then `make app-run` to start the bot

## Via Systemd service
1. Setup [venv](https://docs.python.org/3/library/venv.html)
   and install requirements (`pip install -r requirements.txt`)
2. Configure and start [PostgreSQL](https://www.postgresql.org/)
3. Rename `.env.example` to `.env` and configure it
4. Run database migrations with `make migrate` command
5. Configure `telegram-bot.service` ([» Read more](https://gist.github.com/comhad/de830d6d1b7ae1f165b925492e79eac8))

## Update database tables structure
**Make migration script:**

    make migration message=MESSAGE_WHAT_THE_MIGRATION_DOES

**Run migrations:**

    make migrate

# Used technologies:
- [Aiogram 3.x](https://github.com/aiogram/aiogram) (Telegram Bot framework)
- [PostgreSQL](https://www.postgresql.org/) (database)
- [SQLAlchemy](https://docs.sqlalchemy.org/en/20/) (working with database from Python)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) (lightweight database migration tool)
