import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import csv
import time

# --- CONFIGURATION ---
INPUT_FILE = 'Lead List - Sheet11.csv'
OUTPUT_FILE = 'found_emails.csv'

# WHICH COLUMN IS THE WEBSITE IN?
# A=0, B=1, C=2, D=3, E=4
WEBSITE_COLUMN_INDEX = 3  # <--- Updated for Column D

EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

def fix_url(url):
    """Ensures the URL has http:// and cleans up messy text"""
    url = url.strip()
    if not url: return None
    
    # If it doesn't have a dot (like .com or .co.uk), it's probably not a URL
    if "." not in url:
        return None
        
    if not url.startswith(('http://', 'https://')):
        return 'https://' + url
    return url

def extract_emails_from_site(url):
    print(f"🔍 Scanning: {url}...")
    headers = {'User-Agent': 'Mozilla/5.0'} # Pretend to be a real browser
    try:
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        emails = set(re.findall(EMAIL_REGEX, response.text))
        
        # Search Contact Page
        for link in soup.find_all('a', href=True):
            if re.search(r'contact|about|touch', link.text, re.I):
                contact_link = urljoin(url, link['href'])
                try:
                    contact_res = requests.get(contact_link, timeout=10, headers=headers)
                    contact_emails = re.findall(EMAIL_REGEX, contact_res.text)
                    emails.update(contact_emails)
                except:
                    pass 
                break 
            
        return list(emails)
    except Exception as e:
        print(f"   ⚠️ Could not connect: {e}")
        return []

def main():
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Website', 'Found Emails', 'Name Guess'])

        try:
            with open(INPUT_FILE, 'r', encoding='utf-8-sig') as infile:
                reader = csv.reader(infile)
                
                for row_number, row in enumerate(reader):
                    # Skip empty rows
                    if not row: continue
                    
                    # Safety check: Does Column E exist in this row?
                    if len(row) <= WEBSITE_COLUMN_INDEX:
                        print(f"   ⏩ Row {row_number+1}: Missing data in Column E. Skipping.")
                        continue

                    raw_data = row[WEBSITE_COLUMN_INDEX] # Read Column E
                    
                    # 1. VALIDATE: Is this actually a URL?
                    url = fix_url(raw_data)
                    
                    if not url:
                        print(f"   ⏩ Row {row_number+1}: '{raw_data}' is not a valid URL. Skipping.")
                        continue

                    # 2. RUN EXTRACTION
                    found_emails = extract_emails_from_site(url)
                    
                    # 3. NAME GUESSING
                    name_guess = ""
                    if found_emails:
                        first_email = found_emails[0]
                        user_part = first_email.split('@')[0]
                        if '.' not in user_part and 'info' not in user_part and 'admin' not in user_part:
                            name_guess = user_part.capitalize()
                    
                    email_str = ", ".join(found_emails)
                    if email_str:
                        print(f"   ✅ FOUND: {email_str}")
                    else:
                        print(f"   ❌ No emails found.")

                    writer.writerow([url, email_str, name_guess])
                    time.sleep(1) # Be polite to servers

            print(f"\n🎉 Done! Results saved to {OUTPUT_FILE}")

        except FileNotFoundError:
            print(f"❌ Error: Could not find '{INPUT_FILE}'.")

if __name__ == "__main__":
    main()