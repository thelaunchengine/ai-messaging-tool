#!/usr/bin/env python3

def add_celery_logging_config():
    # Read the celery_app.py file
    with open('celery_app.py', 'r') as f:
        content = f.read()
    
    # Add logging configuration after the imports
    old_imports = '''from celery import Celery
import os
from dotenv import load_dotenv'''
    
    new_imports = '''from celery import Celery
import os
import logging
from dotenv import load_dotenv

# Configure logging for Celery
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to stdout/stderr
        logging.FileHandler('celery_worker.log')  # Also log to file
    ]
)'''
    
    if old_imports in content:
        content = content.replace(old_imports, new_imports)
        print("✅ Added logging configuration to Celery app")
    else:
        print("⚠️  Could not find imports to replace")
    
    # Add logging configuration to Celery config
    old_config = '''# Celery configuration
celery_app.conf.update('''
    
    new_config = '''# Celery configuration
celery_app.conf.update('''
    
    if old_config in content:
        # Find the end of the config section and add logging
        config_end = content.find('task_default_routing_key=\'default\',')
        if config_end != -1:
            # Insert logging config before the closing parenthesis
            before_config_end = content[:config_end + len('task_default_routing_key=\'default\','):]
            after_config_end = content[config_end + len('task_default_routing_key=\'default\','):]
            
            # Find the closing parenthesis
            closing_paren = after_config_end.find(')')
            if closing_paren != -1:
                new_content = before_config_end + '''
    # Logging configuration
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    worker_log_color=True,
    worker_redirect_stdouts=True,
    worker_redirect_stdouts_level='INFO',
''' + after_config_end[closing_paren:]
                
                content = new_content
                print("✅ Added logging configuration to Celery config")
            else:
                print("⚠️  Could not find closing parenthesis in config")
        else:
            print("⚠️  Could not find config section to modify")
    else:
        print("⚠️  Could not find Celery config section")
    
    # Write the updated content back
    with open('celery_app.py', 'w') as f:
        f.write(content)
    
    print("\n🎯 Celery logging configuration added!")
    print("🔄 Please restart the backend services to apply the changes")
    return True

if __name__ == "__main__":
    add_celery_logging_config()
