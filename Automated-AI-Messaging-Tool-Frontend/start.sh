#!/bin/sh

# Check if we should skip database migration
if [ "$SKIP_DATABASE_MIGRATION" = "true" ]; then
  echo "⏭️ Skipping database migration (SKIP_DATABASE_MIGRATION=true)"
else
  echo "🔄 Running database migration..."
  node migrate-db.js
fi

# Start the Next.js application
echo "🚀 Starting Next.js application..."
exec node server.js
