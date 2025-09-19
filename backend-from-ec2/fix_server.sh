#!/bin/bash

# Script to fix automatic scraping on live server
echo "🔧 Fixing automatic scraping on live server..."

# SSH into server and make changes
ssh xb3353@103.215.159.51 << 'EOF'

cd ~/Automated-AI-Messaging-Tool-Backend

echo "📁 Current directory: $(pwd)"

# Backup the original file
cp celery_tasks/file_tasks.py celery_tasks/fileawah_tasks.py.backup

# Check if the automatic triggering code exists exists
if grep -q "AUTOMATICALLY TRIGGER SCRAPING" celery_tasks/file_tasks.py; then
    echo "✅ Automatic scraping trigger already exists"
else
    echo "❌ Automatic scraping trigger missing - adding it now..."
    
    # Find the line where scraping job is created and add automatic triggering
    sed -i '/Created scraping job for file upload/a\
                    # AUTOMATICALLY TRIGGER SCRAPING TASK\
                    from celery_tasks.scraping_tasks import scrape_websites_task\
                    \
                    # Get website URLs for scraping\
                    website_urls = [website["url"] for website in websites]\
                    \
                    # Start scraping task automatically\
                    scraping_task = scrape_websites_task.delay(\
                        file_upload_id=file_upload_id,\
                        user_id=user_id,\
                        websites=website_urls\
                    )\
                    \
                    logger.info(f"Automatically triggered scraping task {scraping_task.id} for {len(website_urls)} websites")\
                    ' celery_tasks/file_tasks.py
fi

# Also fix the syntax error in scraping_tasks.py
echo "🔧 Fixing syntax error in scraping_tasks.py..."
sed -i 's/    except Exception as e:/            except Exception as e:/' celery_tasks/scraping_tasks.py

# Restart the services
echo "🔄 Restarting services..."
pkill -f "celery.*worker"
sleep 2

# Start Celery worker
source venv/bin/activate
celery -A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker@%h --max-tasks-per-child=1000 > logs/celery.log 2>&1 &

echo "✅ Changes applied and services restarted"
echo "📊 Check logs with: tail -f logs/celery.log"

EOF

echo "🎉 Server fixes completed!" 