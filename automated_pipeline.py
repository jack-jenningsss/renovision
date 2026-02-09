import pandas as pd
import requests
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# --- 1. CONFIGURATION ---
INPUT_CSV = 'companies_roofing_hartlepool.csv'         # The file you get from Google Maps
GOOGLE_SHEET_NAME = "Renovision Leads" # Matches your actual Google Sheet Name
TARGET_SERVICE = "Roofing"          # The niche you are targeting
COMPANIES_HOUSE_API_KEY = "8a046685-eeee-4f76-8f98-817bc7430ca7" # ⚠️ PASTE YOUR KEY HERE

# --- 2. EMAIL EXTRACTOR ---
def extract_emails(url):
    """Visits a website and finds emails using the Contact page logic."""
    if not isinstance(url, str) or "." not in url: return []
    if not url.startswith('http'): url = 'https://' + url
    
    print(f"   🔎 Scanning site: {url}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url, timeout=10, headers=headers)
        
        # Regex search on Homepage
        emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', resp.text))
        
        # If none, try finding a Contact link
        if not emails:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                if re.search(r'contact|about|touch', link.text, re.I):
                    contact_url = urljoin(url, link['href'])
                    try:
                        c_resp = requests.get(contact_url, timeout=10, headers=headers)
                        emails.update(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', c_resp.text))
                    except: pass
                    break
        
        # Filter out junk emails (images, example, wix)
        valid_emails = [e for e in emails if not any(x in e.lower() for x in ['png', 'jpg', 'jpeg', 'wix', 'example', 'sentry', 'u00'])]
        return list(valid_emails)
    except Exception as e:
        print(f"   ⚠️ Site Error: {e}")
        return []

# --- 3. COMPANIES HOUSE LOOKUP ---
def get_director_from_api(company_name):
    """Queries Companies House API for the active director's first name."""
    api_url = "https://api.company-information.service.gov.uk"
    auth = (COMPANIES_HOUSE_API_KEY, '') # Basic Auth
    
    # Clean the name for better search (remove Ltd, Limited)
    clean_name = re.sub(r'(?i)ltd|limited|co\.|uk', '', company_name).strip()
    
    try:
        # A. Search for company
        search_res = requests.get(f"{api_url}/search/companies", params={'q': clean_name}, auth=auth)
        if search_res.status_code != 200: return None
        
        results = search_res.json().get('items', [])
        if not results: return None
        
        # Use the first valid match
        company_number = results[0]['company_number']
        
        # B. Get Officers (Directors)
        officers_res = requests.get(f"{api_url}/company/{company_number}/officers", auth=auth)
        if officers_res.status_code != 200: return None
        
        officers = officers_res.json().get('items', [])
        
        for officer in officers:
            # Must be an active DIRECTOR (not secretary, not resigned)
            if 'resigned_on' not in officer and officer.get('officer_role') == 'director':
                raw_name = officer['name'] # Format: "SURNAME, Firstname Middle"
                
                if "," in raw_name:
                    parts = raw_name.split(',')
                    first_name = parts[1].strip().split(' ')[0] # Grab first word after comma
                    return first_name.title() # Return "Dave"
                
    except Exception as e:
        print(f"   ⚠️ API Error: {e}")
        
    return None # Return None if not found

# --- 4. MAIN PIPELINE ---
def run_pipeline():
    print("🚀 Starting Mega-Pipeline...")
    
    # A. Load Data Miner CSV
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{INPUT_CSV}' in this folder.")
        return

    # B. Map Data Miner Columns -> Our Logic
    # Data Miner usually gives: 'Name', 'Phone', 'Email', 'Website', 'Address'
    # We rename them to be consistent
    column_map = {
        'Name': 'Business Name',
        'Website': 'Website',
        'Phone': 'Phone'
    }
    df = df.rename(columns=column_map)
    
    # Ensure 'Business Name' and 'Website' exist
    if 'Business Name' not in df.columns or 'Website' not in df.columns:
        print("❌ Error: CSV missing 'Name' or 'Website' columns. Check Data Miner headers.")
        return

    # C. Filter 1: Drop empty websites immediately
    df = df.dropna(subset=['Website'])
    df = df[df['Website'].str.contains(r'\.', na=False)] # Must look like a URL
    print(f"📋 Processing {len(df)} companies with websites...")

    valid_leads = []

    # D. Iterate through rows
    for index, row in df.iterrows():
        company_name = str(row['Business Name']).strip()
        website = str(row['Website']).strip()
        phone = str(row.get('Phone', ''))
        
        print(f"➡️ Processing: {company_name}")

        # STEP 2: Get Email
        emails = extract_emails(website)
        if not emails:
            print(f"   ❌ Dropping: No email found.")
            continue
        email = emails[0] # Take first valid email

        # STEP 5: Get Director Name (Strict Mode)
        director_name = get_director_from_api(company_name)
        if not director_name:
            print(f"   ❌ Dropping: No Director found on Companies House.")
            continue # STRICT DROP as requested
        
        print(f"   ✅ Success: Found {director_name} @ {company_name}")

        # Prepare Row for Google Sheet
        # Structure: Business Name, Email, Lead Name, Services, Phone, Website, Status
        valid_leads.append([
            company_name,       # Business Name
            email,              # Email
            director_name,      # Lead Name
            TARGET_SERVICE,     # Services
            phone,              # Phone
            website,            # Website
            "Not Sent Email"          # Status (Ready for Make.com)
        ])
        
        # Polite delay for APIs
        time.sleep(1)

    if not valid_leads:
        print("⚠️ No valid leads found. Pipeline finished.")
        return

    # E. Upload to Google Sheets (Step 4)
    print("💾 Connecting to Google Sheets...")
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open(GOOGLE_SHEET_NAME).sheet1
        
        # Deduplication Check
        existing_data = sheet.get_all_records()
        existing_emails = set(str(row['Email']).lower() for row in existing_data)
        
        final_upload = []
        for lead in valid_leads:
            lead_email = lead[1].lower()
            if lead_email not in existing_emails:
                final_upload.append(lead)
                existing_emails.add(lead_email) # Prevent duplicates within this batch
            else:
                print(f"   🚫 Skipping duplicate: {lead[0]}")

        if final_upload:
            sheet.append_rows(final_upload)
            print(f"🎉 Uploaded {len(final_upload)} new leads to Google Sheets!")
        else:
            print("✅ Pipeline finished, but all leads were duplicates.")

    except Exception as e:
        print(f"❌ Google Sheets Error: {e}")

if __name__ == "__main__":
    run_pipeline()