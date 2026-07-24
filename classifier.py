#!/usr/bin/env python3
"""
Claude-powered Classification Engine
Classifies regulatory updates into categories, impact levels, and explains why it matters
"""

import json
import os
from datetime import datetime
import anthropic


# Classification schema
CATEGORIES = [
    "Succession & Estate Planning",
    "FEMA & Foreign Exchange",
    "RBI & Monetary Policy",
    "IFSCA & GIFT City",
    "Cross-Border Taxation",
    "Trusts & Foundations",
    "SEBI & Family Office",
    "Insolvency & Bankruptcy",
    "Stamp Duty & Property Law",
    "PMLA & KYC",
    "International Tax (OECD/CRS/FATCA)",
    "Other"
]

JURISDICTIONS = [
    "India",
    "Singapore",
    "UAE",
    "US",
    "UK",
    "Switzerland",
    "Liechtenstein",
    "Jersey",
    "Mauritius",
    "Luxembourg",
    "Other"
]

IMPACT_LEVELS = [
    "Critical",  # Law amended, RBI notification, major regulation
    "Important",  # Circulars, consultations, significant rulings
    "Informational"  # Commentary, speeches, industry articles
]


def classify_item(item: dict, client: anthropic.Anthropic) -> dict:
    """Use Claude to classify a single regulatory item"""
    
    prompt = f"""You are a regulatory intelligence expert for a wealth management firm's Private Client Solutions desk.

Classify this regulatory update:

Title: {item['title']}
Source: {item['source']}
URL: {item['url']}
Published: {item['published']}
Summary: {item.get('summary', 'No summary available')}

TASK:
1. Assign ONE primary category from this list:
{', '.join(CATEGORIES)}

2. Assign ONE primary jurisdiction from this list:
{', '.join(JURISDICTIONS)}

3. Assign ONE impact level:
{', '.join(IMPACT_LEVELS)}

4. Write a 1-line summary (under 15 words) capturing the regulatory change
5. Write 2-3 sentences explaining "Why it matters" for estate/succession/wealth planning

Respond ONLY as valid JSON with no other text:
{{
    "category": "...",
    "jurisdiction": "...",
    "impact_level": "...",
    "one_line_summary": "...",
    "why_it_matters": "...",
    "confidence": 0.0-1.0
}}
"""
    
    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse response
        response_text = message.content[0].text
        
        # Clean up markdown code fences if present
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        classification = json.loads(response_text)
        return classification
        
    except json.JSONDecodeError as e:
        print(f"JSON parse error for '{item['title']}': {e}")
        return {
            "category": "Other",
            "jurisdiction": "India",
            "impact_level": "Informational",
            "one_line_summary": item['title'][:50],
            "why_it_matters": "Requires manual review",
            "confidence": 0.3
        }
    except Exception as e:
        print(f"Classification error for '{item['title']}': {e}")
        return {
            "category": "Other",
            "jurisdiction": "India",
            "impact_level": "Informational",
            "one_line_summary": item['title'][:50],
            "why_it_matters": "Classification failed - requires manual review",
            "confidence": 0.0
        }


def classify_all_items(data_file: str):
    """Classify all unclassified items in updates.json"""
    
    # Initialize Anthropic client
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        return
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Load existing data
    if not os.path.exists(data_file):
        print(f"No data file found at {data_file}")
        return
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    updates = data.get('updates', [])
    print(f"Total items to process: {len(updates)}")
    
    # Classify items that don't have classification yet
    classified_count = 0
    for i, item in enumerate(updates):
        if 'classification' not in item or not item['classification']:
            print(f"[{i+1}/{len(updates)}] Classifying: {item['title'][:60]}...")
            
            classification = classify_item(item, client)
            item['classification'] = classification
            classified_count += 1
            
            # Add classified timestamp
            item['classified_at'] = datetime.now().isoformat()
    
    print(f"\nClassified {classified_count} new items")
    
    # Save updated data
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✓ Saved classified updates to {data_file}")


def main():
    data_file = 'data/updates.json'
    print("=" * 60)
    print(f"Claude Classification Engine: {datetime.now()}")
    print("=" * 60)
    classify_all_items(data_file)
    print("=" * 60)
    print("Classification completed")
    print("=" * 60)


if __name__ == '__main__':
    main()
