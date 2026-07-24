#!/usr/bin/env python3
"""
Regulatory Intelligence Scraper
Pulls from RBI, IFSCA, SEBI, CBDT, India Code, Supreme Court
Runs daily via GitHub Actions at 8 AM IST
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import hashlib
import requests
from bs4 import BeautifulSoup
import feedparser

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegulatoryScraperError(Exception):
    pass


class SourceScraper:
    """Base class for scraping regulatory sources"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 10
        self.items = []
    
    def dedupe_key(self, title: str, url: str) -> str:
        """Generate a deduplication key"""
        combined = f"{title}:{url}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def parse_rss(self, url: str, source_name: str, source_type: str) -> List[Dict]:
        """Parse RSS feed"""
        try:
            feed = feedparser.parse(url)
            items = []
            for entry in feed.entries[:15]:  # Limit to 15 most recent
                item = {
                    'title': entry.get('title', 'Untitled'),
                    'url': entry.get('link', ''),
                    'published': entry.get('published', datetime.now().isoformat()),
                    'source': source_name,
                    'source_type': source_type,
                    'summary': entry.get('summary', '')[:500],
                }
                items.append(item)
            logger.info(f"✓ {source_name}: {len(items)} items from RSS")
            return items
        except Exception as e:
            logger.error(f"✗ {source_name} RSS parse failed: {e}")
            return []
    
    def scrape_html(self, url: str, selector: str, source_name: str, source_type: str) -> List[Dict]:
        """Generic HTML scraper"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            items = []
            
            for elem in soup.select(selector)[:15]:
                link = elem.find('a')
                if not link:
                    continue
                
                item = {
                    'title': link.get_text(strip=True),
                    'url': link.get('href', ''),
                    'published': datetime.now().isoformat(),
                    'source': source_name,
                    'source_type': source_type,
                    'summary': '',
                }
                
                # Ensure absolute URL
                if item['url'] and not item['url'].startswith('http'):
                    item['url'] = url.rstrip('/') + '/' + item['url'].lstrip('/')
                
                if item['url']:
                    items.append(item)
            
            logger.info(f"✓ {source_name}: {len(items)} items from HTML")
            return items
        except Exception as e:
            logger.error(f"✗ {source_name} HTML scrape failed: {e}")
            return []


class RBIScraper(SourceScraper):
    """RBI notifications, circulars, FEMA updates"""
    
    def scrape(self) -> List[Dict]:
        items = []
        
        # RBI Press Releases (RSS available, but also scrape main page)
        press_url = "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"
        items.extend(self.scrape_html(
            press_url,
            'table tr td a',
            'RBI - Press Releases',
            'official'
        ))
        
        # RBI Notifications (FEMA related)
        notif_url = "https://www.rbi.org.in/scripts/NotificationUser.aspx?Id=11858"
        items.extend(self.scrape_html(
            notif_url,
            'table tr td a',
            'RBI - FEMA Notifications',
            'official'
        ))
        
        # RBI Circulars
        circ_url = "https://www.rbi.org.in/scripts/BS_CircularIndexDisplay.aspx?Id=10822"
        items.extend(self.scrape_html(
            circ_url,
            'table tr td a',
            'RBI - Circulars',
            'official'
        ))
        
        return items


class IFSCAScraper(SourceScraper):
    """IFSCA circulars and press releases for GIFT City"""
    
    def scrape(self) -> List[Dict]:
        items = []
        
        # IFSCA Circulars
        circ_url = "https://www.ifsca.gov.in/Circular"
        items.extend(self.scrape_html(
            circ_url,
            'div.news-item a',
            'IFSCA - Circulars',
            'official'
        ))
        
        # IFSCA Press Releases
        press_url = "https://www.ifsca.gov.in/PressRelease"
        items.extend(self.scrape_html(
            press_url,
            'div.news-item a',
            'IFSCA - Press Releases',
            'official'
        ))
        
        # IFSCA Notifications/Orders (if available)
        notif_url = "https://www.ifsca.gov.in/Notification"
        items.extend(self.scrape_html(
            notif_url,
            'div.news-item a',
            'IFSCA - Notifications',
            'official'
        ))
        
        return items


class SEBIScraper(SourceScraper):
    """SEBI notifications relevant to family offices and AIFs"""
    
    def scrape(self) -> List[Dict]:
        items = []
        
        # SEBI Circulars
        circ_url = "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?action=showpath&val=584"
        items.extend(self.scrape_html(
            circ_url,
            'a[href*="circular"]',
            'SEBI - Circulars',
            'official'
        ))
        
        return items


class CBDTScraper(SourceScraper):
    """Income Tax circulars and notifications"""
    
    def scrape(self) -> List[Dict]:
        items = []
        
        # CBDT Circulars
        circ_url = "https://www.incometaxindia.gov.in/communications/circulars"
        items.extend(self.scrape_html(
            circ_url,
            'table tr td a',
            'CBDT - Circulars',
            'official'
        ))
        
        return items


class SupremeCourtScraper(SourceScraper):
    """Supreme Court judgments relevant to succession and estate planning"""
    
    def scrape(self) -> List[Dict]:
        items = []
        
        # Supreme Court orders (recent)
        orders_url = "https://main.sci.gov.in/supremecourt/2024/orders/"
        items.extend(self.scrape_html(
            orders_url,
            'table tr td a',
            'Supreme Court - Orders',
            'official'
        ))
        
        return items


class IndiaCodeScraper(SourceScraper):
    """Track Indian Succession Act, Hindu Succession Act for amendments"""
    
    def scrape(self) -> List[Dict]:
        items = []
        
        # Indian Succession Act
        isa_url = "https://www.indiacode.nic.in/handle/123456789/2318"
        items.extend(self.scrape_html(
            isa_url,
            'table tr td a',
            'India Code - Indian Succession Act',
            'official'
        ))
        
        # Hindu Succession Act
        hsa_url = "https://www.indiacode.nic.in/handle/123456789/2318"
        items.extend(self.scrape_html(
            hsa_url,
            'table tr td a',
            'India Code - Hindu Succession Act',
            'official'
        ))
        
        return items


def scrape_all_sources() -> List[Dict]:
    """Run all scrapers and combine results"""
    all_items = []
    
    scrapers = [
        ('RBI', RBIScraper()),
        ('IFSCA', IFSCAScraper()),
        ('SEBI', SEBIScraper()),
        ('CBDT', CBDTScraper()),
        ('Supreme Court', SupremeCourtScraper()),
        ('India Code', IndiaCodeScraper()),
    ]
    
    logger.info("=" * 60)
    logger.info(f"Regulatory Scrape Started: {datetime.now()}")
    logger.info("=" * 60)
    
    for name, scraper in scrapers:
        try:
            items = scraper.scrape()
            all_items.extend(items)
        except Exception as e:
            logger.error(f"✗ {name} scraper failed: {e}")
    
    logger.info(f"\nTotal items scraped: {len(all_items)}")
    return all_items


def deduplicate_items(new_items: List[Dict], existing_items: List[Dict]) -> List[Dict]:
    """Remove duplicates based on URL and title hash"""
    existing_keys = {
        hashlib.md5(f"{item['title']}:{item['url']}".encode()).hexdigest()
        for item in existing_items
    }
    
    deduplicated = []
    for item in new_items:
        key = hashlib.md5(f"{item['title']}:{item['url']}".encode()).hexdigest()
        if key not in existing_keys:
            deduplicated.append(item)
    
    logger.info(f"After deduplication: {len(deduplicated)} new items")
    return deduplicated


def load_existing_data(filepath: str) -> Dict:
    """Load existing updates.json"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {'updates': [], 'last_scraped': None}
    return {'updates': [], 'last_scraped': None}


def save_data(filepath: str, data: Dict):
    """Save updates.json"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    logger.info(f"✓ Saved {len(data['updates'])} items to {filepath}")


def main():
    # Paths
    data_file = 'data/updates.json'
    os.makedirs('data', exist_ok=True)
    
    # Load existing data
    existing_data = load_existing_data(data_file)
    existing_items = existing_data.get('updates', [])
    
    # Scrape all sources
    new_items = scrape_all_sources()
    
    # Deduplicate
    fresh_items = deduplicate_items(new_items, existing_items)
    
    # Combine: new items go to top
    all_items = fresh_items + existing_items
    
    # Keep only last 500 items to prevent unbounded growth
    all_items = all_items[:500]
    
    # Update data
    data = {
        'updates': all_items,
        'last_scraped': datetime.now().isoformat(),
        'total_count': len(all_items)
    }
    
    # Save
    save_data(data_file, data)
    
    logger.info("=" * 60)
    logger.info("Scrape completed successfully")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
