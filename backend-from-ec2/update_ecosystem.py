#!/usr/bin/env python3

def update_ecosystem():
    # Read the ecosystem.config.js file
    with open('ecosystem.config.js', 'r') as f:
        content = f.read()
    
    # Read the .env file to get environment variables
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
        print(f"✅ Loaded {len(env_vars)} environment variables from .env file")
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False
    
    # Update the env section for each app to include the .env variables
    for app_name in ['fastapi-backend', 'celery-worker-1', 'celery-worker-2', 'celery-monitor']:
        # Find the env section for this app
        env_start = content.find(f"name: '{app_name}'")
        if env_start != -1:
            # Find the env section after this app
            env_section_start = content.find("env: {", env_start)
            if env_section_start != -1:
                # Find the end of the env section
                env_section_end = content.find("}", env_section_start)
                if env_section_end != -1:
                    # Build new env section
                    new_env = "      env: {\n"
                    new_env += "        NODE_ENV: 'production',\n"
                    for key, value in env_vars.items():
                        new_env += f"        {key}: '{value}',\n"
                    new_env += "      }"
                    
                    # Replace the old env section
                    old_env = content[env_section_start:env_section_end + 1]
                    content = content.replace(old_env, new_env)
                    print(f"✅ Updated env section for {app_name}")
                else:
                    print(f"⚠️  Could not find end of env section for {app_name}")
            else:
                print(f"⚠️  Could not find env section for {app_name}")
        else:
            print(f"⚠️  Could not find app {app_name}")
    
    # Write the updated content back
    with open('ecosystem.config.js', 'w') as f:
        f.write(content)
    
    print("\n🎯 Ecosystem configuration updated successfully!")
    print("🔄 Please restart PM2 to apply the new environment variables")
    return True

if __name__ == "__main__":
    update_ecosystem()
