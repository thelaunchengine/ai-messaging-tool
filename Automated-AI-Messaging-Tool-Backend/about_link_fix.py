import re

# Read the current file
with open('scraping_tasks.py', 'r') as f:
    content = f.read()

# Find the about links section
pattern = r'# Look for about links\n    about_links = \[\]\n    for a in soup\.find_all\('a', href=True\):\n        href = a\['href'\]\.lower\(\)\n        link_text = a\.get_text\(\)\.lower\(\)\n        \n        if any\(word in href for word in \['about', 'about-us', 'aboutus', 'company'\]\):\n            about_links\.append\(urljoin\(base_url, a\['href'\]\)\)\n        elif any\(word in link_text for word in \['about', 'about us', 'company'\]\):\n            about_links\.append\(urljoin\(base_url, a\['href'\]\)\)\n    \n    if about_links:\n        about_url = about_links\[0\]  # Take the first about link'

replacement = '''# Look for about links
    about_links = []
    for a in soup.find_all('a', href=True):
        href = a['href'].lower()
        link_text = a.get_text().lower()
        
        if any(word in href for word in ['about', 'about-us', 'aboutus', 'company']):
            about_links.append(urljoin(base_url, a['href']))
        elif any(word in link_text for word in ['about', 'about us', 'company']):
            about_links.append(urljoin(base_url, a['href']))
    
    # Prioritize website's own about pages over external links
    own_about_links = [link for link in about_links if base_url.replace('https://', '').replace('http://', '').replace('www.', '') in link.replace('https://', '').replace('http://', '').replace('www.', '')]
    if own_about_links:
        about_url = own_about_links[0]  # Take the first own about link
    elif about_links:
        about_url = about_links[0]  # Fallback to any about link'''

# Replace the pattern
content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Write back to file
with open('scraping_tasks.py', 'w') as f:
    f.write(content)

print('About link prioritization fixed!')
