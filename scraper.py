import os
import json
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import time

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

def analyze_with_gemini(text, title):
    prompt = f"""
    You are a regulatory analyst for a Private Wealth and Estate Planning desk. Analyze this update:
    Categories allowed: "Succession & Estate Planning", "FEMA / Foreign Capital", "IFSCA & GIFT City", "Cross-border Taxation", "Trusts & Foundations", "General Housekeeping". 
    Impact Levels: "High", "Medium", "Low".

    Title: {title}
    Text: {text[:2000]}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "category": {"type": "STRING"},
                    "impact_level": {"type": "STRING"},
                    "summary": {"type": "STRING"},
                    "why_it_matters": {"type": "STRING"},
                    "affected_entities": {"type": "ARRAY", "items": {"type": "STRING"}}
                },
                "required": ["category", "impact_level", "summary", "why_it_matters", "affected_entities"]
            }
        }
    }
    
    try:
        # Sleep for 2 seconds to avoid hitting Gemini API rate limits
        time.sleep(2)
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        return json.loads(response.json()['candidates'][0]['content']['parts'][0]['text'])
    except Exception as e:
        print(f"Gemini Analysis Failed: {e}")
        return {"category": "General Housekeeping", "impact_level": "Low", "summary": "Automated summary failed.", "why_it_matters": "Requires manual review.", "affected_entities": []}

def fetch_rbi():
    print("Fetching RBI...")
    urls = [
        "https://www.rbi.org.in/Scripts/NotificationUser.aspx",
        "https://www.rbi.org.in/scripts/BS_ViewMasterDirections.aspx",
        "https://www.rbi.org.in/scripts/Fs_AmendmentDirections.aspx",
        "https://www.rbi.org.in/scripts/DraftNotificationsGuildelines.aspx"
    ]
    updates = []
    success = False

    for url in urls:
        try:
            req = requests.get(url, headers=HEADERS, timeout=15)
            req.raise_for_status()
            success = True
            soup = BeautifulSoup(req.content, 'html.parser')
            
            # RBI generally uses tables with class 'tablebg'
            links = soup.select('table.tablebg a')
            if not links:
                links = soup.select('.link2') # Fallback class used on some RBI pages

            for link in links[:2]: # Top 2 per page
                title = link.text.strip()
                href = link.get('href', '')
                if not href or 'javascript' in href.lower():
                    continue
                
                full_url = href if href.startswith('http') else f"https://www.rbi.org.in/Scripts/{href}"
                analysis = analyze_with_gemini(f"Extracted from {url}", title)
                
                updates.append({
                    "id": full_url[-15:], 
                    "published_date": datetime.now().strftime("%Y-%m-%d"), 
                    "source": "RBI", 
                    "title": title[:150] + "..." if len(title) > 150 else title, 
                    "url": full_url, 
                    "classification": analysis
                })
        except Exception as e:
            print(f"Failed parsing RBI URL {url}: {e}")

    return success, updates

def fetch_ifsca():
    print("Fetching IFSCA...")
    urls = [
        "https://ifsca.gov.in/Legal/Index/zcGvy-Iqfcg=",
        "https://ifsca.gov.in/Legal/Index/ogGPf3wx5GE=",
        "https://ifsca.gov.in/Legal/Index/sKCVtbX6J9o="
    ]
    updates = []
    success = False

    for url in urls:
        try:
            req = requests.get(url, headers=HEADERS, timeout=15)
            req.raise_for_status()
            success = True
            soup = BeautifulSoup(req.content, 'html.parser')
            
            # IFSCA stores documents in a standard data table
            rows = soup.select('table tbody tr')
            for row in rows[:2]:
                title_tag = row.select_one('td:nth-child(2)')
                link_tag = row.select_one('td a')
                
                if title_tag and link_tag:
                    title = title_tag.text.strip()
                    href = link_tag.get('href', '')
                    full_url = href if href.startswith('http') else f"https://ifsca.gov.in{href}"
                    
                    analysis = analyze_with_gemini("IFSCA PDF Document", title)
                    updates.append({
                        "id": full_url[-15:], 
                        "published_date": datetime.now().strftime("%Y-%m-%d"), 
                        "source": "IFSCA", 
                        "title": title, 
                        "url": full_url, 
                        "classification": analysis
                    })
        except Exception as e:
            print(f"Failed parsing IFSCA URL {url}: {e}")

    return success, updates

def fetch_sebi():
    print("Fetching SEBI...")
    urls = [
        "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=7&smid=0",
        "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingLegal=yes&sid=1&ssid=1&smid=0",
        "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=3&smid=0"
    ]
    updates = []
    success = False

    for url in urls:
        try:
            req = requests.get(url, headers=HEADERS, timeout=15)
            req.raise_for_status()
            success = True
            soup = BeautifulSoup(req.content, 'html.parser')
            
            for row in soup.select('.table tbody tr')[:2]:
                a_tag = row.select_one('a')
                if a_tag:
                    title = a_tag.text.strip()
                    full_url = a_tag.get('href', '')
                    
                    analysis = analyze_with_gemini("SEBI Document", title)
                    updates.append({
                        "id": full_url[-15:], 
                        "published_date": datetime.now().strftime("%Y-%m-%d"), 
                        "source": "SEBI", 
                        "title": title, 
                        "url": full_url, 
                        "classification": analysis
                    })
        except Exception as e:
            print(f"Failed parsing SEBI URL {url}: {e}")

    return success, updates

def fetch_cbdt():
    print("Fetching CBDT (Tax)...")
    updates = []
    try:
        req = requests.get("https://www.incometaxindia.gov.in/circular-rss-feed/-/asset_publisher/bxhj/rss", headers=HEADERS, timeout=15)
        req.raise_for_status()
        feed = feedparser.parse(req.content)
        for entry in feed.entries[:2]:
            analysis = analyze_with_gemini(entry.description, entry.title)
            updates.append({
                "id": entry.link[-15:], 
                "published_date": datetime.now().strftime("%Y-%m-%d"), 
                "source": "CBDT", 
                "title": entry.title, 
                "url": entry.link, 
                "classification": analysis
            })
        return True, updates
    except Exception as e:
        print(f"CBDT fetch failed: {e}")
        return False, updates

def main():
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        return

    all_new_updates = []
    scanned_sources = []

    # Run scrapers and track successes
    rbi_ok, rbi_data = fetch_rbi()
    if rbi_ok: scanned_sources.append("RBI")
    all_new_updates.extend(rbi_data)

    ifsca_ok, ifsca_data = fetch_ifsca()
    if ifsca_ok: scanned_sources.append("IFSCA")
    all_new_updates.extend(ifsca_data)

    sebi_ok, sebi_data = fetch_sebi()
    if sebi_ok: scanned_sources.append("SEBI")
    all_new_updates.extend(sebi_data)
    
    cbdt_ok, cbdt_data = fetch_cbdt()
    if cbdt_ok: scanned_sources.append("CBDT")
    all_new_updates.extend(cbdt_data)
    
    # Load existing data
    data_file = "data.json"
    existing_updates = []
    
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            try: 
                data = json.load(f)
                if isinstance(data, dict):
                    existing_updates = data.get("updates", [])
                elif isinstance(data, list):
                    existing_updates = data
            except: 
                pass
                
    # Deduplicate based on URL
    existing_urls = {item.get('url') for item in existing_updates if isinstance(item, dict) and 'url' in item}
    added = 0
    
    for update in all_new_updates:
        if update['url'] not in existing_urls:
            existing_updates.insert(0, update)
            added += 1
            
    # Save perfectly formatted JSON for Next.js frontend
    output_data = {
        "last_scraped": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources_scanned": scanned_sources,
        "updates": existing_updates
    }
            
    with open(data_file, "w") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Run complete. Scanned {scanned_sources}. Added {added} new updates.")

if __name__ == "__main__":
    main()