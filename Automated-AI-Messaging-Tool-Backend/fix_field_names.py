#!/usr/bin/env python3

def fix_field_names():
    # Read the message_generator.py file
    with open('ai/message_generator.py', 'r') as f:
        content = f.read()
    
    # Fix 1: Replace company_name with companyName
    old_company = "company_name=website_data.get('company_name', '')"
    new_company = "company_name=website_data.get('companyName', '')"
    
    if old_company in content:
        content = content.replace(old_company, new_company)
        print("✅ Fixed company_name field")
    else:
        print("⚠️  Could not find company_name field to replace")
    
    # Fix 2: Replace business_type with businessType
    old_business = "business_type=website_data.get('business_type', '')"
    new_business = "business_type=website_data.get('businessType', '')"
    
    if old_business in content:
        content = content.replace(old_business, new_business)
        print("✅ Fixed business_type field")
    else:
        print("⚠️  Could not find business_type field to replace")
    
    # Fix 3: Replace about_us_content with aboutUsContent
    old_about = "about_us_content=website_data.get('about_us_content', '')[:500]"
    new_about = "about_us_content=website_data.get('aboutUsContent', '')[:500]"
    
    if old_about in content:
        content = content.replace(old_about, new_about)
        print("✅ Fixed about_us_content field")
    else:
        print("⚠️  Could not find about_us_content field to replace")
    
    # Fix 4: Replace in fallback messages
    old_fallback_company = "website_data.get('company_name', 'Valued Business')"
    new_fallback_company = "website_data.get('companyName', 'Valued Business')"
    
    if old_fallback_company in content:
        content = content.replace(old_fallback_company, new_fallback_company)
        print("✅ Fixed fallback company_name field")
    else:
        print("⚠️  Could not find fallback company_name field to replace")
    
    old_fallback_industry = "website_data.get('industry', 'business')"
    new_fallback_industry = "website_data.get('industry', 'business')"
    
    if old_fallback_industry in content:
        content = content.replace(old_fallback_industry, new_fallback_industry)
        print("✅ Fixed fallback industry field")
    else:
        print("⚠️  Could not find fallback industry field to replace")
    
    # Write the updated content back
    with open('ai/message_generator.py', 'w') as f:
        f.write(content)
    
    print("\n🎯 Field name mismatches fixed successfully!")
    print("🔄 Please restart the backend services to apply the changes")
    return True

if __name__ == "__main__":
    fix_field_names()
