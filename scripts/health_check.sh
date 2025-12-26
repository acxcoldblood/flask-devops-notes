#!/bin/sh
set -e

echo "Waiting for app to be ready..."

count=0
while [ $count -lt 10 ]; do
  if curl -sf http://localhost:5000/health > /dev/null; then
    echo "Health check passed"
    exit 0
  fi
  sleep 3
  count=$((count + 1))
done

echo "Health check failed"
exit 1
