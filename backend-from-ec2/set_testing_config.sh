#!/bin/bash

# Testing Configuration Script for AI Messaging Tool
# This script helps set environment variables for testing mode

echo "=== AI Messaging Tool - Testing Configuration ==="
echo ""

# Function to set environment variables
set_testing_config() {
    local testing_mode=$1
    local max_messages=$2
    
    echo "Setting testing configuration..."
    echo "TESTING_MODE_ENABLED=$testing_mode"
    echo "MAX_AI_MESSAGES_PER_FILE=$max_messages"
    echo ""
    
    # Export for current session
    export TESTING_MODE_ENABLED=$testing_mode
    export MAX_AI_MESSAGES_PER_FILE=$max_messages
    
    # Add to .bashrc for persistence (optional)
    read -p "Add to .bashrc for persistence? (y/n): " add_to_bashrc
    if [[ $add_to_bashrc == "y" || $add_to_bashrc == "Y" ]]; then
        # Remove existing entries
        sed -i '/export TESTING_MODE_ENABLED/d' ~/.bashrc
        sed -i '/export MAX_AI_MESSAGES_PER_FILE/d' ~/.bashrc
        
        # Add new entries
        echo "export TESTING_MODE_ENABLED=$testing_mode" >> ~/.bashrc
        echo "export MAX_AI_MESSAGES_PER_FILE=$max_messages" >> ~/.bashrc
        
        echo "Configuration added to .bashrc"
        echo "Please run 'source ~/.bashrc' or restart your terminal"
    fi
    
    echo ""
    echo "Configuration set successfully!"
    echo "Current environment variables:"
    echo "TESTING_MODE_ENABLED: $TESTING_MODE_ENABLED"
    echo "MAX_AI_MESSAGES_PER_FILE: $MAX_AI_MESSAGES_PER_FILE"
}

# Function to show current configuration
show_current_config() {
    echo "Current testing configuration:"
    echo "TESTING_MODE_ENABLED: ${TESTING_MODE_ENABLED:-'not set (default: true)'}"
    echo "MAX_AI_MESSAGES_PER_FILE: ${MAX_AI_MESSAGES_PER_FILE:-'not set (default: 2)'}"
    echo ""
}

# Function to show available options
show_options() {
    echo "Available testing configurations:"
    echo ""
    echo "1. Development Testing (2 messages per file)"
    echo "   - TESTING_MODE_ENABLED=true"
    echo "   - MAX_AI_MESSAGES_PER_FILE=2"
    echo ""
    echo "2. Extended Testing (5 messages per file)"
    echo "   - TESTING_MODE_ENABLED=true"
    echo "   - MAX_AI_MESSAGES_PER_FILE=5"
    echo ""
    echo "3. Staging Testing (10 messages per file)"
    echo "   - TESTING_MODE_ENABLED=true"
    echo "   - MAX_AI_MESSAGES_PER_FILE=10"
    echo ""
    echo "4. Production Mode (unlimited messages)"
    echo "   - TESTING_MODE_ENABLED=false"
    echo "   - MAX_AI_MESSAGES_PER_FILE=unlimited"
    echo ""
    echo "5. Custom Configuration"
    echo "   - Set your own values"
    echo ""
}

# Main menu
while true; do
    echo "Please select an option:"
    echo "1. Development Testing (2 messages per file)"
    echo "2. Extended Testing (5 messages per file)"
    echo "3. Staging Testing (10 messages per file)"
    echo "4. Production Mode (unlimited messages)"
    echo "5. Custom Configuration"
    echo "6. Show Current Configuration"
    echo "7. Show Available Options"
    echo "8. Exit"
    echo ""
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1)
            set_testing_config "true" "2"
            break
            ;;
        2)
            set_testing_config "true" "5"
            break
            ;;
        3)
            set_testing_config "true" "10"
            break
            ;;
        4)
            set_testing_config "false" "unlimited"
            break
            ;;
        5)
            echo ""
            read -p "Enter TESTING_MODE_ENABLED (true/false): " testing_mode
            read -p "Enter MAX_AI_MESSAGES_PER_FILE (number): " max_messages
            set_testing_config "$testing_mode" "$max_messages"
            break
            ;;
        6)
            show_current_config
            ;;
        7)
            show_options
            ;;
        8)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid choice. Please enter a number between 1 and 8."
            echo ""
            ;;
    esac
done

echo ""
echo "=== Configuration Complete ==="
echo ""
echo "To apply these settings to your Celery workers and backend:"
echo "1. Restart your Celery workers: pm2 restart all"
echo "2. Restart your backend: pm2 restart backend"
echo ""
echo "To verify the configuration:"
echo "curl http://localhost:8000/api/config/testing"
echo ""
echo "Note: Environment variables are set for the current session."
echo "If you added them to .bashrc, they will persist across sessions."
