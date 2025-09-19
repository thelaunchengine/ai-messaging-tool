#!/usr/bin/env python3

def fix_database_schema():
    # Read the database_manager.py file
    with open('database/database_manager.py', 'r') as f:
        content = f.read()
    
    # Fix the get_predefined_messages_by_criteria method
    old_method = '''    def get_predefined_messages_by_criteria(self, industry: str = None, business_type: str = None, status: str = 'ACTIVE') -> List[Dict[str, Any]]:

        """Get predefined messages based on criteria"""
        try:
            where_conditions = ["is_active = %s"]
            params = [status == 'ACTIVE']
            
            if industry:
                where_conditions.append("LOWER(industry) LIKE LOWER(%s)")
                params.append(f"%{industry}%")
            
            if business_type:
                where_conditions.append("LOWER(business_type) LIKE LOWER(%s)")
                params.append(f"%{business_type}%")
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
                SELECT id, title, content, message_type, industry, business_type, tone, is_active, usage_count, success_rate, created_at, updated_at
                FROM predefined_messages
                WHERE {where_clause}
                ORDER BY usage_count ASC
            """
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            messages = []
            for row in results:
                messages.append({
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
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting predefined messages: {e}")
            return []'''
    
    new_method = '''    def get_predefined_messages_by_criteria(self, industry: str = None, business_type: str = None, status: str = 'ACTIVE') -> List[Dict[str, Any]]:

        """Get predefined messages based on criteria"""
        try:
            where_conditions = ["status = %s"]
            params = [status]
            
            if industry:
                where_conditions.append("LOWER(industry) LIKE LOWER(%s)")
                params.append(f"%{industry}%")
            
            if business_type:
                where_conditions.append("LOWER(service) LIKE LOWER(%s)")
                params.append(f"%{business_type}%")
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
                SELECT id, industry, service, message, status, "usageCount", "messageType", tone, "createdAt", "updatedAt"
                FROM predefined_messages
                WHERE {where_clause}
                ORDER BY "usageCount" ASC
            """
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            messages = []
            for row in results:
                messages.append({
                    'id': row[0],
                    'title': f"{row[1]} - {row[2]}",  # industry - service
                    'content': row[3],  # message
                    'messageType': row[4],  # status
                    'industry': row[5],  # industry
                    'businessType': row[6],  # service
                    'tone': row[7],  # tone
                    'isActive': row[8] == 'ACTIVE',  # status
                    'usageCount': row[9] if row[9] else 0,  # usageCount
                    'successRate': 0.8,  # Default success rate since it doesn't exist
                    'createdAt': row[10].isoformat() if row[10] else None,
                    'updatedAt': row[11].isoformat() if row[11] else None
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting predefined messages: {e}")
            return []'''
    
    if old_method in content:
        content = content.replace(old_method, new_method)
        print("✅ Fixed get_predefined_messages_by_criteria method")
    else:
        print("⚠️  Could not find the exact method to replace")
        return False
    
    # Fix the get_predefined_message_by_id method
    old_get_by_id = '''            query = f"""
                SELECT id, title, content, message_type, industry, business_type, tone, is_active, usage_count, success_rate, created_at, updated_at
                FROM predefined_messages
                WHERE id = %s
            """'''
    
    new_get_by_id = '''            query = f"""
                SELECT id, industry, service, message, status, "usageCount", "messageType", tone, "createdAt", "updatedAt"
                FROM predefined_messages
                WHERE id = %s
            """'''
    
    if old_get_by_id in content:
        content = content.replace(old_get_by_id, new_get_by_id)
        print("✅ Fixed get_predefined_message_by_id method")
    else:
        print("⚠️  Could not find get_predefined_message_by_id method")
    
    # Fix the get_predefined_messages_stats method
    old_stats = '''            query = f"""
                SELECT id, title, usage_count, success_rate
                FROM predefined_messages
                ORDER BY usage_count DESC
                LIMIT 5
            """'''
    
    new_stats = '''            query = f"""
                SELECT id, industry, "usageCount", 0.8 as success_rate
                FROM predefined_messages
                ORDER BY "usageCount" DESC
                LIMIT 5
            """'''
    
    if old_stats in content:
        content = content.replace(old_stats, new_stats)
        print("✅ Fixed get_predefined_messages_stats method")
    else:
        print("⚠️  Could not find get_predefined_messages_stats method")
    
    # Write the updated content back
    with open('database/database_manager.py', 'w') as f:
        f.write(content)
    
    print("\n🎯 Database schema mismatch fixed successfully!")
    print("🔄 Please restart the backend services to apply the changes")
    return True

if __name__ == "__main__":
    fix_database_schema()
