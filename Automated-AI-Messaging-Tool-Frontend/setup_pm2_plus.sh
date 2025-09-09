#!/bin/bash

# PM2 Plus Setup Script
echo "Setting up PM2 Plus..."

# Link to PM2 Plus with provided credentials
echo "y" | pm2 link qcn5vrlk47vtdg8 r9vknqanlx2ln2p

# Check if linking was successful
if [ $? -eq 0 ]; then
    echo "✅ PM2 Plus linked successfully!"
    echo "🌐 Access your dashboard at: https://app.pm2.io"
    echo "📊 You can now monitor all your services from the web dashboard"
else
    echo "❌ PM2 Plus linking failed"
fi

# Show current PM2 status
echo ""
echo "📋 Current PM2 Services:"
pm2 list 