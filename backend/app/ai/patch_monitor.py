"""
Patch Monitor — GW2_WvWBuilder v4.3

Monitors Guild Wars 2 official sources for patch notes and balance changes.
Automatically detects nerfs, buffs, and reworks affecting WvW specializations.
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urljoin
import urllib.request
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class SimplePatchParser(HTMLParser):
    """Lightweight HTML parser for patch notes."""
    
    def __init__(self):
        super().__init__()
        self.text_chunks: List[str] = []
        self.links: set = set()
        
    def handle_data(self, data):
        text = data.strip()
        if text:
            self.text_chunks.append(text)
    
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, value in attrs:
                if attr == "href" and value:
                    self.links.add(value)
    
    def get_text(self) -> str:
        return " ".join(self.text_chunks)


def fetch_patch_page(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch patch notes page with extended timeout."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "GW2_WvWBuilder/4.3 (Patch Monitor)",
                "Accept": "text/html,application/xhtml+xml",
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def extract_patch_changes(text: str, source: str) -> List[Dict]:
    """Extract balance changes from patch notes text.
    
    Detects:
    - Nerfs (reduced, decreased, removed, nerfed)
    - Buffs (increased, improved, buffed, enhanced)
    - Reworks (reworked, changed, updated, adjusted)
    """
    from app.core.kb.specs_reference import get_all_elite_specs
    
    changes = []
    elite_specs = get_all_elite_specs()
    
    # Keywords for change detection
    nerf_keywords = [
        r"\breduced\b", r"\bdecreased\b", r"\bremoved\b", r"\bnerfed\b",
        r"\blowered\b", r"\bweakened\b", r"\bless\s+effective\b"
    ]
    
    buff_keywords = [
        r"\bincreased\b", r"\bimproved\b", r"\bbuffed\b", r"\benhanced\b",
        r"\bstrengthened\b", r"\bmore\s+effective\b", r"\braised\b"
    ]
    
    rework_keywords = [
        r"\breworked\b", r"\bchanged\b", r"\bupdated\b", r"\badjusted\b",
        r"\bmodified\b", r"\breplaced\b", r"\bredesigned\b"
    ]
    
    lines = text.lower().split("\n")
    
    for line in lines:
        # Check if line mentions a specialization
        for spec in elite_specs:
            if spec.lower() in line:
                change_type = "unknown"
                impact = line[:200]  # Extract context
                
                # Detect change type
                if any(re.search(pattern, line) for pattern in nerf_keywords):
                    change_type = "nerf"
                elif any(re.search(pattern, line) for pattern in buff_keywords):
                    change_type = "buff"
                elif any(re.search(pattern, line) for pattern in rework_keywords):
                    change_type = "rework"
                else:
                    continue  # Skip if no change detected
                
                # Extract magnitude if present (e.g., "15%", "2 seconds")
                magnitude_match = re.search(r"(\d+)%|\b(\d+)\s+(second|stacks?)\b", line)
                magnitude = magnitude_match.group(0) if magnitude_match else None
                
                changes.append({
                    "date": datetime.now().isoformat()[:10],
                    "spec": spec,
                    "change_type": change_type,
                    "impact": impact.strip(),
                    "magnitude": magnitude,
                    "source": source,
                })
    
    return changes


def monitor_gw2_wiki() -> List[Dict]:
    """Monitor GW2 Wiki for recent patch notes."""
    logger.info("Monitoring GW2 Wiki for patch notes...")
    base_url = "https://wiki.guildwars2.com"
    patch_urls = [
        f"{base_url}/wiki/Game_updates",
        f"{base_url}/wiki/Game_updates/2025",
        f"{base_url}/wiki/Balance_updates",
    ]
    
    all_changes = []
    
    for url in patch_urls:
        time.sleep(1.0)  # Rate limiting
        html = fetch_patch_page(url)
        if not html:
            continue
        
        parser = SimplePatchParser()
        parser.feed(html)
        text = parser.get_text()
        
        changes = extract_patch_changes(text, "gw2wiki")
        all_changes.extend(changes)
    
    logger.info(f"GW2 Wiki: {len(all_changes)} changes detected")
    return all_changes


def parse_rss_feed(url: str) -> List[Dict]:
    """Parse RSS feed and extract forum posts.
    
    Args:
        url: RSS feed URL
        
    Returns:
        List of dict with title, description, link, pubDate
    """
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "GW2_WvWBuilder/4.3 (RSS Reader)",
                "Accept": "application/rss+xml, application/xml",
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read()
        
        # Parse XML
        root = ET.fromstring(xml_data)
        items = []
        
        # Handle RSS 2.0 format
        for item in root.findall(".//item"):
            title_elem = item.find("title")
            desc_elem = item.find("description")
            link_elem = item.find("link")
            pub_date_elem = item.find("pubDate")
            
            if title_elem is not None:
                items.append({
                    "title": title_elem.text or "",
                    "description": desc_elem.text or "" if desc_elem is not None else "",
                    "link": link_elem.text or "" if link_elem is not None else "",
                    "pub_date": pub_date_elem.text or "" if pub_date_elem is not None else "",
                })
        
        return items
    except Exception as e:
        logger.warning(f"Failed to parse RSS feed {url}: {e}")
        return []


def is_wvw_relevant(text: str) -> bool:
    """Check if forum post is WvW-relevant.
    
    Args:
        text: Post title + description
        
    Returns:
        True if WvW-relevant, False otherwise
    """
    wvw_keywords = [
        r"\bwvw\b", r"\bworld vs world\b", r"\bmcm\b", r"\bmists\b",
        r"\bzerg\b", r"\bhavoc\b", r"\broaming\b", r"\bsquad\b",
        r"\bcommander\b", r"\bkeep\b", r"\btower\b", r"\bsiege\b",
    ]
    
    # Check if any WvW keyword is present
    text_lower = text.lower()
    for pattern in wvw_keywords:
        if re.search(pattern, text_lower):
            return True
    
    # Check for balance/patch keywords (general changes)
    balance_keywords = [
        r"\bbalance\b", r"\bpatch\b", r"\bupdate\b", r"\bnotes\b",
        r"\bnerf\b", r"\bbuff\b", r"\brework\b", r"\bchanges\b",
    ]
    
    for pattern in balance_keywords:
        if re.search(pattern, text_lower):
            return True
    
    return False


def monitor_gw2_forum() -> List[Dict]:
    """Monitor GW2 Official Forum via RSS feeds."""
    logger.info("Monitoring GW2 Forum via RSS...")
    
    rss_feeds = [
        "https://en-forum.guildwars2.com/categories/game-release-notes/feed.rss",
        "https://en-forum.guildwars2.com/discussions/feed.rss",
    ]
    
    all_changes = []
    
    for feed_url in rss_feeds:
        time.sleep(1.0)  # Rate limiting
        items = parse_rss_feed(feed_url)
        
        for item in items:
            # Combine title and description for analysis
            combined_text = f"{item['title']} {item['description']}"
            
            # Filter: only WvW-relevant posts
            if not is_wvw_relevant(combined_text):
                continue
            
            # Extract balance changes from post
            changes = extract_patch_changes(combined_text, "forum")
            
            # Add source link to each change
            for change in changes:
                change["source_url"] = item.get("link", "")
                change["post_title"] = item.get("title", "")
            
            all_changes.extend(changes)
    
    logger.info(f"GW2 Forum RSS: {len(all_changes)} changes detected")
    return all_changes


def monitor_reddit_gw2() -> List[Dict]:
    """Monitor r/Guildwars2 for patch discussions (simplified)."""
    logger.info("Monitoring Reddit for patch discussions...")
    # Note: Reddit requires API keys for proper access
    # This is a simplified version using public HTML
    reddit_url = "https://www.reddit.com/r/Guildwars2/search/?q=patch+notes+OR+balance&sort=new&restrict_sr=1"
    
    all_changes = []
    html = fetch_patch_page(reddit_url)
    if not html:
        logger.info("Reddit: Skipped (API required for reliable access)")
        return all_changes
    
    # Very basic extraction (limited without API)
    parser = SimplePatchParser()
    parser.feed(html)
    text = parser.get_text()
    
    # Only extract if clear patch mention
    if "patch" in text.lower() or "balance" in text.lower():
        changes = extract_patch_changes(text, "reddit")
        all_changes.extend(changes[:5])  # Limit to avoid noise
    
    logger.info(f"Reddit: {len(all_changes)} changes detected")
    return all_changes


def monitor_all_sources() -> List[Dict]:
    """Monitor all configured sources for patch notes."""
    logger.info("=" * 70)
    logger.info("Patch Monitor Cycle Started")
    logger.info("=" * 70)
    
    all_changes = []
    
    try:
        wiki_changes = monitor_gw2_wiki()
        all_changes.extend(wiki_changes)
    except Exception as e:
        logger.error(f"GW2 Wiki monitoring failed: {e}")
    
    try:
        forum_changes = monitor_gw2_forum()
        all_changes.extend(forum_changes)
    except Exception as e:
        logger.error(f"Forum monitoring failed: {e}")
    
    try:
        reddit_changes = monitor_reddit_gw2()
        all_changes.extend(reddit_changes)
    except Exception as e:
        logger.error(f"Reddit monitoring failed: {e}")
    
    # Deduplicate changes
    unique_changes = []
    seen = set()
    for change in all_changes:
        key = (change["spec"], change["change_type"], change.get("magnitude"))
        if key not in seen:
            seen.add(key)
            unique_changes.append(change)
    
    logger.info("=" * 70)
    logger.info(f"Patch Monitor Complete: {len(unique_changes)} unique changes")
    logger.info("=" * 70)
    
    return unique_changes


def filter_recent_changes(changes: List[Dict], days: int = 7) -> List[Dict]:
    """Filter changes to only those from the last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    recent = []
    
    for change in changes:
        try:
            change_date = datetime.fromisoformat(change["date"])
            if change_date >= cutoff:
                recent.append(change)
        except (KeyError, ValueError):
            continue
    
    return recent
