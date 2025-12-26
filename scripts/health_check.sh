#!/bin/sh
set -e

echo "Waiting for app to be ready..."

for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -sf http://localhost/health > /dev/null; then
    echo "Health check passed"
    exit 0
  fi
  sleep 3
done

echo "Health check failed"
exit 1
