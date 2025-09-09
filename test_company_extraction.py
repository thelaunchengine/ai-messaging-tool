#!/usr/bin/env python3
import re

def clean_company_name(title):
    """Clean company name from various title formats"""
    
    # Start with the original title
    cleaned = title
    
    # Pattern 1: Remove "Find a X Agent in Y, Z | Company" format
    # Example: "Find a Farmers Insurance® Agent in Santa Clarita, CA | Farmers Insurance®"
    cleaned = re.sub(r'^Find a [^|]+Agent in [^|]+\s*[-|]\s*', '', cleaned, flags=re.IGNORECASE)
    
    # Pattern 2: Remove business category prefixes
    # Example: "Used Cars | Albuquerque, NM | One Express Motors LLC"
    cleaned = re.sub(r'^(Used Cars|New Cars|Auto Sales|Car Dealership|Auto Dealership)\s*[-|]\s*', '', cleaned, flags=re.IGNORECASE)
    
    # Pattern 3: Remove location patterns (state abbreviations) - more aggressive
    # Example: "Albuquerque, NM | One Express Motors LLC"
    cleaned = re.sub(r'\s*[-|]\s*[A-Za-z\s,]+(?:NM|CA|TX|NY|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|CO|TN|IN|MO|MD|MN|WI|AL|SC|LA|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|WV|NE|ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY)\s*[-|]?', '', cleaned, flags=re.IGNORECASE)
    
    # Pattern 4: Remove city, state patterns at the beginning
    # Example: "New York, NY | Business Solutions Inc"
    cleaned = re.sub(r'^[A-Za-z\s,]+(?:NM|CA|TX|NY|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|CO|TN|IN|MO|MD|MN|WI|AL|SC|LA|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|WV|NE|ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY)\s*[-|]\s*', '', cleaned, flags=re.IGNORECASE)
    
    # Pattern 5: Remove common suffixes
    # Example: "A&R Auto Sales LLC - Home"
    cleaned = re.sub(r'\s*[-|]\s*(Home|Welcome|Official Site|Official Website|Dealership|Auto|Cars).*$', '', cleaned, flags=re.IGNORECASE)
    
    # Pattern 6: Remove "Welcome to" prefixes
    # Example: "Welcome to ABC Company | Official Site"
    cleaned = re.sub(r'^Welcome to\s+', '', cleaned, flags=re.IGNORECASE)
    
    # Pattern 7: Remove "Official Site" and similar
    cleaned = re.sub(r'\s*[-|]\s*Official Site.*$', '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra separators
    cleaned = re.sub(r'\s*[-|]\s*$', '', cleaned)
    cleaned = re.sub(r'^\s*[-|]\s*', '', cleaned)
    
    # Final cleanup
    cleaned = cleaned.strip()
    
    return cleaned

def test_company_name_extraction():
    """Test the improved company name extraction logic"""
    
    # Test cases
    test_cases = [
        "Used Cars | Albuquerque, NM | One Express Motors LLC",
        "Find a Farmers Insurance® Agent in Santa Clarita, CA | Farmers Insurance®",
        "A&R Auto Sales LLC - Home",
        "Welcome to ABC Company | Official Site",
        "New York, NY | Business Solutions Inc",
        "One Express Motors LLC",
        "Farmers Insurance",
        "A&R Auto Sales LLC"
    ]
    
    print("🧪 Testing Company Name Extraction Logic\n")
    
    for i, title in enumerate(test_cases, 1):
        print(f"Test {i}: '{title}'")
        
        cleaned_title = clean_company_name(title)
        
        # Check if it looks like a company name
        is_valid = (cleaned_title and 
                   len(cleaned_title) < 100 and 
                   not re.match(r'^[A-Za-z\s,]+(?:NM|CA|TX|NY|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|CO|TN|IN|MO|MD|MN|WI|AL|SC|LA|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|WV|NE|ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY)$', cleaned_title))
        
        print(f"   Cleaned: '{cleaned_title}'")
        print(f"   Valid: {'✅' if is_valid else '❌'}")
        print()

if __name__ == "__main__":
    test_company_name_extraction()
