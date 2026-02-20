#!/bin/sh

# Wait for database if using postgres
if [ "$DB_TYPE" = "postgres" ]; then
    echo "Waiting for postgres..."
    # You could add a more robust wait-for-it script here if needed
    sleep 5
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
