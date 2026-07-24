import os
import json
import requests
import feedparser
from datetime import datetime

# Securely load the Gemini API Key from GitHub Actions
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

def analyze_with_gemini(text, title):
    prompt = f"""
    You are a regulatory analyst for a Private Wealth and Estate Planning desk. Analyze the following regulatory update.
    
    Categories allowed: "Succession & Estate Planning", "FEMA / Foreign Capital", "IFSCA & GIFT City", "Cross-border Taxation", "Trusts & Foundations", "General Housekeeping". 
    Impact Levels: "High", "Medium", "Low".

    Title: {title}
    Text: {text}
    """
    
    # This payload forces Gemini to respond strictly in your JSON dashboard format
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "category": {"type": "STRING"},
                    "impact_level": {"type": "STRING"},
                    "summary": {"type": "STRING", "description": "1 sentence summary"},
                    "why_it_matters": {"type": "STRING", "description": "2 sentences focusing on HNI/Family Office impact"},
                    "affected_entities": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    }
                },
                "required": ["category", "impact_level", "summary", "why_it_matters", "affected_entities"]
            }
        }
    }
    
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        result_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        return json.loads(result_text)
    except Exception as e:
        print(f"Failed to analyze with Gemini: {e}")
        return {
            "category": "General Housekeeping",
            "impact_level": "Low",
            "summary": "Automated summary failed. Please review the source directly.",
            "why_it_matters": "Requires manual review.",
            "affected_entities": []
        }

def fetch_rbi_updates():
    print("Fetching RBI RSS feed...")
    url = "https://www.rbi.org.in/Scripts/rss.aspx"
    feed = feedparser.parse(url)
    
    updates = []
    # Grab the top 3 latest updates for the daily run to keep it fast
    for entry in feed.entries[:3]:
        print(f"Analyzing: {entry.title}")
        analysis = analyze_with_gemini(entry.description, entry.title)
        
        update = {
            "id": entry.link.split('=')[-1] if '=' in entry.link else entry.link[-10:],
            "published_date": datetime.now().strftime("%Y-%m-%d"),
            "source": "RBI",
            "source_type": "Press Release",
            "title": entry.title,
            "url": entry.link,
            "classification": {
                "category": analysis.get("category", "General Housekeeping"),
                "impact_level": analysis.get("impact_level", "Low"),
                "jurisdiction": ["India"]
            },
            "analysis": {
                "summary": analysis.get("summary", ""),
                "why_it_matters": analysis.get("why_it_matters", ""),
                "affected_entities": analysis.get("affected_entities", [])
            }
        }
        updates.append(update)
    return updates

def main():
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        return

    new_updates = fetch_rbi_updates()
    
    # Load existing dashboard data
    data_file = "data.json"
    existing_data = []
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
                
    # Deduplicate by URL so the dashboard doesn't show the same update twice
    existing_urls = {item['url'] for item in existing_data}
    added_count = 0
    
    for update in new_updates:
        if update['url'] not in existing_urls:
            existing_data.insert(0, update)
            added_count += 1
            
    # Save the fresh intelligence back to your repository
    with open(data_file, "w") as f:
        json.dump(existing_data, f, indent=2)
        
    print(f"Run complete. Added {added_count} new regulatory updates.")

if __name__ == "__main__":
    main()