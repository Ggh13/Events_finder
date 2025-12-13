#!/usr/bin/env bash

set -e

echo "Run apply migrations"
alembic -c ./alembic.ini upgrade head
echo "Migrations applied"

exec "$@"