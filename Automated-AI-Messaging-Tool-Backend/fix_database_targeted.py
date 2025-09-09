#!/usr/bin/env python3

def fix_database_targeted():
    # Read the database_manager.py file
    with open('database/database_manager.py', 'r') as f:
        content = f.read()
    
    # Fix 1: Replace the column names in the SELECT query
    old_select = "SELECT id, title, content, message_type, industry, business_type, tone, is_active, usage_count, success_rate, created_at, updated_at"
    new_select = 'SELECT id, industry, service, message, status, "usageCount", "messageType", tone, "createdAt", "updatedAt"'
    
    if old_select in content:
        content = content.replace(old_select, new_select)
        print("✅ Fixed SELECT query columns")
    else:
        print("⚠️  Could not find the SELECT query to replace")
    
    # Fix 2: Replace the WHERE condition
    old_where = "is_active = %s"
    new_where = "status = %s"
    
    if old_where in content:
        content = content.replace(old_where, new_where)
        print("✅ Fixed WHERE condition")
    else:
        print("⚠️  Could not find the WHERE condition to replace")
    
    # Fix 3: Replace the parameter logic
    old_params = "params = [status == 'ACTIVE']"
    new_params = "params = [status]"
    
    if old_params in content:
        content = content.replace(old_params, new_params)
        print("✅ Fixed parameter logic")
    else:
        print("⚠️  Could not find the parameter logic to replace")
    
    # Fix 4: Replace business_type with service in the WHERE condition
    old_business_where = "LOWER(business_type) LIKE LOWER(%s)"
    new_business_where = "LOWER(service) LIKE LOWER(%s)"
    
    if old_business_where in content:
        content = content.replace(old_business_where, new_business_where)
        print("✅ Fixed business_type WHERE condition")
    else:
        print("⚠️  Could not find the business_type WHERE condition to replace")
    
    # Fix 5: Replace the ORDER BY clause
    old_order = "ORDER BY usage_count ASC"
    new_order = 'ORDER BY "usageCount" ASC'
    
    if old_order in content:
        content = content.replace(old_order, new_order)
        print("✅ Fixed ORDER BY clause")
    else:
        print("⚠️  Could not find the ORDER BY clause to replace")
    
    # Fix 6: Replace the row mapping to match new schema
    old_row_mapping = """                messages.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'messageType': row[3],
                    'industry': row[4],
                    'businessType': row[5],
                    'tone': row[6],
                    'isActive': row[7],
                    'usageCount': row[8],
                    'successRate': float(row[9]) if row[9] else 0.0,
                    'createdAt': row[10].isoformat() if row[10] else None,
                    'updatedAt': row[11].isoformat() if row[11] else None
                })"""
    
    new_row_mapping = """                messages.append({
                    'id': row[0],
                    'title': f"{row[1]} - {row[2]}",  # industry - service
                    'content': row[3],  # message
                    'messageType': row[4],  # status
                    'industry': row[5],  # industry
                    'businessType': row[6],  # service
                    'tone': row[7],  # tone
                    'isActive': row[8] == 'ACTIVE',  # status
                    'usageCount': row[9] if row[9] else 0,  # usageCount
                    'successRate': 0.8,  # Default success rate
                    'createdAt': row[10].isoformat() if row[10] else None,
                    'updatedAt': row[11].isoformat() if row[11] else None
                })"""
    
    if old_row_mapping in content:
        content = content.replace(old_row_mapping, new_row_mapping)
        print("✅ Fixed row mapping")
    else:
        print("⚠️  Could not find the row mapping to replace")
    
    # Write the updated content back
    with open('database/database_manager.py', 'w') as f:
        f.write(content)
    
    print("\n🎯 Database schema fixes applied!")
    print("🔄 Please restart the backend services to apply the changes")
    return True

if __name__ == "__main__":
    fix_database_targeted()
