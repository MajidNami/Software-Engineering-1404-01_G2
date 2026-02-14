#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate

echo "Starting services..."
python presentation/grpc/server/grpc_server.py &
python -m http.server 2022 &
python manage.py runserver 0.0.0.0:2004 &

wait
