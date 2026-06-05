#!/bin/sh
docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env-Internal up -d --build