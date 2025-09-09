#!/bin/bash

# Simple script to copy updated files to remote server
SERVER="xb3353@103.215.159.51"
SERVER_PATH="/home/xb3353/Automated-AI-Messaging-Tool-Backend"
PASSWORD="aZ9LdgAPsW6"

echo "Copying updated database_manager.py to remote server..."

# Copy the updated database manager
echo "$PASSWORD" | sshpass -p "$PASSWORD" scp database/database_manager.py $SERVER:$SERVER_PATH/database/

echo "Copying updated main.py to remote server..."

# Copy the updated main.py
echo "$PASSWORD" | sshpass -p "$PASSWORD" scp main.py $SERVER:$SERVER_PATH/

echo "Files copied successfully!"

echo "Now checking PM2 status on remote server..."
echo "$PASSWORD" | sshpass -p "$PASSWORD" ssh $SERVER "cd $SERVER_PATH && sudo pm2 status"
