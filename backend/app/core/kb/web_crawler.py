from __future__ import annotations

import logging
import re
import time
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
import urllib.request
from html.parser import HTMLParser

logger = logging.getLogger(__name__)


class SimpleHTMLParser(HTMLParser):
    """Lightweight HTML parser to extract text and links."""
    
    def __init__(self):
        super().__init__()
        self.text_chunks: List[str] = []
        self.links: Set[str] = set()
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag == "a":
            for attr, value in attrs:
                if attr == "href" and value:
                    self.links.add(value)
    
    def handle_data(self, data):
        if self.current_tag not in ["script", "style", "noscript"]:
            text = data.strip()
            if text:
                self.text_chunks.append(text)
    
    def get_text(self) -> str:
        return " ".join(self.text_chunks)


def fetch_page(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch HTML content from URL with timeout and error handling."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "GW2_WvWBuilder/4.1 (Educational/Research)",
                "Accept": "text/html,application/xhtml+xml",
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def extract_build_info(text: str, source: str) -> Dict[str, any]:
    """Extract build-related information from page text.
    
    Filters for WvW-specific content and scores relevance.
    """
    from app.core.kb.specs_reference import get_all_elite_specs, is_elite_spec
    
    info = {
        "source": source,
        "professions": [],
        "specializations": [],
        "elite_specializations": [],
        "core_specializations": [],
        "boons": [],
        "roles": [],
        "synergies": [],
        "is_wvw": False,
        "wvw_score": 0.0,
    }
    
    # Common GW2 professions
    professions = [
        "Guardian", "Warrior", "Engineer", "Ranger", "Thief",
        "Elementalist", "Mesmer", "Necromancer", "Revenant"
    ]
    
    # Get all elite specs from reference
    elite_specs = get_all_elite_specs()
    
    # Boons
    boons = [
        "quickness", "alacrity", "stability", "resistance",
        "protection", "might", "fury", "aegis", "vigor", "swiftness"
    ]
    
    # Roles
    roles = [
        "support", "dps", "healer", "tank", "boon", "cleanse",
        "cc", "burst", "sustain", "mobility", "stealth"
    ]
    
    text_lower = text.lower()
    
    # Extract professions
    for prof in professions:
        if prof.lower() in text_lower:
            info["professions"].append(prof)
    
    # Extract specializations (elite only for now)
    for spec in elite_specs:
        if spec.lower() in text_lower:
            info["specializations"].append(spec)
            info["elite_specializations"].append(spec)
    
    # Extract boons
    for boon in boons:
        if boon in text_lower:
            info["boons"].append(boon)
    
    # Extract roles
    for role in roles:
        if role in text_lower:
            info["roles"].append(role)
    
    # Extract synergy mentions (simple pattern)
    synergy_patterns = [
        r"(firebrand|scrapper|herald|tempest|scourge)\s+(?:and|with|\+)\s+(firebrand|scrapper|herald|tempest|scourge)",
        r"synergy\s+(?:with|between)\s+(\w+)\s+(?:and|with)\s+(\w+)",
    ]
    
    for pattern in synergy_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) >= 2:
                pair = (match.group(1).capitalize(), match.group(2).capitalize())
                info["synergies"].append(pair)
    
    # Detect WvW-specific content
    wvw_keywords = [
        "wvw", "world vs world", "world versus world", "mcm", "mists",
        "zerg", "havoc", "roaming", "squad", "commander", "tag",
        "keep", "tower", "smc", "stonemist", "garrison", "bay", "hills",
        "borderlands", "eternal battlegrounds", "red bl", "blue bl", "green bl",
        "pirate ship", "blob", "push", "siege", "trebuchet", "catapult",
        "boon strip", "boon corrupt", "stability stack", "resistance"
    ]
    
    pve_keywords = [
        "raid", "fractal", "strike", "dungeon", "cm", "challenge mote",
        "boss", "enrage", "dps benchmark", "golem", "training area",
        "instanced", "10-man", "5-man", "encounter", "phase"
    ]
    
    # Score WvW relevance
    wvw_score = 0.0
    for keyword in wvw_keywords:
        if keyword in text_lower:
            wvw_score += 1.0
    
    # Penalize PvE content
    for keyword in pve_keywords:
        if keyword in text_lower:
            wvw_score -= 2.0
    
    # Normalize score
    info["wvw_score"] = wvw_score
    info["is_wvw"] = wvw_score > 0
    
    return info


def crawl_metabattle_wvw() -> List[Dict]:
    """Crawl MetaBattle WvW builds."""
    logger.info("Crawling MetaBattle WvW builds...")
    base_url = "https://metabattle.com"
    start_url = f"{base_url}/wiki/Category:World_vs_World_builds"
    
    builds = []
    html = fetch_page(start_url)
    if not html:
        return builds
    
    parser = SimpleHTMLParser()
    parser.feed(html)
    
    # Extract build links
    build_links = [
        urljoin(base_url, link)
        for link in parser.links
        if "/wiki/" in link and "Build:" in link
    ][:20]  # Limit to 20 builds
    
    for link in build_links:
        time.sleep(0.5)  # Rate limiting
        page_html = fetch_page(link)
        if page_html:
            page_parser = SimpleHTMLParser()
            page_parser.feed(page_html)
            text = page_parser.get_text()
            info = extract_build_info(text, "metabattle")
            info["url"] = link
            builds.append(info)
    
    logger.info(f"Crawled {len(builds)} builds from MetaBattle")
    return builds


def crawl_hardstuck_wvw() -> List[Dict]:
    """Crawl Hardstuck WvW builds."""
    logger.info("Crawling Hardstuck WvW builds...")
    base_url = "https://hardstuck.gg"
    start_url = f"{base_url}/gw2/builds/?t=wvw"  # WvW filter
    
    builds = []
    html = fetch_page(start_url)
    if not html:
        return builds
    
    parser = SimpleHTMLParser()
    parser.feed(html)
    text = parser.get_text()
    
    info = extract_build_info(text, "hardstuck")
    info["url"] = start_url
    builds.append(info)
    
    logger.info(f"Crawled Hardstuck WvW builds")
    return builds


def crawl_snowcrows_wvw() -> List[Dict]:
    """Crawl Snow Crows WvW builds."""
    logger.info("Crawling Snow Crows WvW builds...")
    base_url = "https://snowcrows.com"
    start_url = f"{base_url}/builds/wvw"  # WvW section
    
    builds = []
    html = fetch_page(start_url)
    if not html:
        return builds
    
    parser = SimpleHTMLParser()
    parser.feed(html)
    text = parser.get_text()
    
    info = extract_build_info(text, "snowcrows")
    info["url"] = start_url
    builds.append(info)
    
    logger.info(f"Crawled Snow Crows WvW builds")
    return builds


def crawl_gw2_wiki_professions() -> List[Dict]:
    """Crawl GW2 Wiki profession pages."""
    logger.info("Crawling GW2 Wiki professions...")
    base_url = "https://wiki.guildwars2.com"
    
    professions = [
        "Guardian", "Warrior", "Engineer", "Ranger", "Thief",
        "Elementalist", "Mesmer", "Necromancer", "Revenant"
    ]
    
    profession_data = []
    for prof in professions:
        url = f"{base_url}/wiki/{prof}"
        time.sleep(0.5)
        html = fetch_page(url)
        if html:
            parser = SimpleHTMLParser()
            parser.feed(html)
            text = parser.get_text()
            info = extract_build_info(text, "gw2wiki")
            info["url"] = url
            info["profession"] = prof
            profession_data.append(info)
    
    logger.info(f"Crawled {len(profession_data)} profession pages from GW2 Wiki")
    return profession_data


def crawl_gw2mists() -> List[Dict]:
    """Crawl GW2 Mists builds."""
    logger.info("Crawling GW2 Mists builds...")
    base_url = "https://gw2mists.com"
    start_url = f"{base_url}/builds"
    
    builds = []
    html = fetch_page(start_url)
    if not html:
        return builds
    
    parser = SimpleHTMLParser()
    parser.feed(html)
    text = parser.get_text()
    
    # Extract main page info
    info = extract_build_info(text, "gw2mists")
    info["url"] = start_url
    builds.append(info)
    
    # Try to extract build links (simplified, could be improved)
    build_links = [
        urljoin(base_url, link)
        for link in parser.links
        if "/builds/" in link and link != "/builds"
    ][:15]  # Limit to 15 builds
    
    for link in build_links:
        time.sleep(0.5)
        page_html = fetch_page(link)
        if page_html:
            page_parser = SimpleHTMLParser()
            page_parser.feed(page_html)
            page_text = page_parser.get_text()
            page_info = extract_build_info(page_text, "gw2mists")
            page_info["url"] = link
            builds.append(page_info)
    
    logger.info(f"Crawled {len(builds)} builds from GW2 Mists")
    return builds


def crawl_google_sheets_wvw() -> List[Dict]:
    """Crawl GW2 WvW Google Spreadsheet (public view)."""
    logger.info("Crawling GW2 WvW Google Spreadsheet...")
    
    # Public HTML export URL
    sheet_id = "1wPCpLzT-wNbU4Zukvc0pG20UgSvxr8zzBJZEwI38HqU"
    gid = "1508949260"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=html&gid={gid}"
    
    builds = []
    html = fetch_page(url, timeout=15)
    if not html:
        logger.warning("Failed to fetch Google Spreadsheet")
        return builds
    
    parser = SimpleHTMLParser()
    parser.feed(html)
    text = parser.get_text()
    
    # Extract build info from spreadsheet text
    info = extract_build_info(text, "google_sheets")
    info["url"] = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid={gid}"
    info["description"] = "GW2 WvW Community Spreadsheet"
    builds.append(info)
    
    logger.info(f"Crawled GW2 WvW Google Spreadsheet")
    return builds


def crawl_all_sources() -> Dict[str, List[Dict]]:
    """Crawl all configured web sources."""
    logger.info("Starting web crawl of GW2 community sources...")
    
    results = {
        "metabattle": [],
        "hardstuck": [],
        "snowcrows": [],
        "gw2wiki": [],
        "gw2mists": [],
        "google_sheets": [],
    }
    
    try:
        results["metabattle"] = crawl_metabattle_wvw()
    except Exception as e:
        logger.error(f"MetaBattle crawl failed: {e}")
    
    try:
        results["hardstuck"] = crawl_hardstuck_wvw()
    except Exception as e:
        logger.error(f"Hardstuck crawl failed: {e}")
    
    try:
        results["snowcrows"] = crawl_snowcrows_wvw()
    except Exception as e:
        logger.error(f"Snow Crows crawl failed: {e}")
    
    try:
        results["gw2wiki"] = crawl_gw2_wiki_professions()
    except Exception as e:
        logger.error(f"GW2 Wiki crawl failed: {e}")
    
    try:
        results["gw2mists"] = crawl_gw2mists()
    except Exception as e:
        logger.error(f"GW2 Mists crawl failed: {e}")
    
    try:
        results["google_sheets"] = crawl_google_sheets_wvw()
    except Exception as e:
        logger.error(f"Google Sheets crawl failed: {e}")
    
    total = sum(len(v) for v in results.values())
    logger.info(f"Web crawl complete: {total} pages indexed")
    
    return results


def extract_synergies_from_crawl(crawl_data: Dict[str, List[Dict]]) -> List[tuple]:
    """Extract synergy pairs from crawled data (WvW-only)."""
    synergies = set()
    
    for source, pages in crawl_data.items():
        for page in pages:
            # Filter: Only process WvW-relevant pages
            if not page.get("is_wvw", False):
                continue
            
            for pair in page.get("synergies", []):
                if len(pair) == 2:
                    # Normalize pair order
                    a, b = sorted([pair[0].lower(), pair[1].lower()])
                    synergies.add((a, b))
    
    return list(synergies)
