import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, parse_qs

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
SERVER = os.getenv("SERVER")
BASE_URL = f"https://{SERVER}.api.mailchimp.com/3.0"

if not API_KEY or not SERVER:
    print("❌ Missing API_KEY or SERVER. Please check your .env file.")
    exit()

headers = {"Authorization": f"Bearer {API_KEY}"}

def fetch_campaigns():
    since_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%S')
    url = f'{BASE_URL}/campaigns'
    params = {'since_send_time': since_date, 'count': 100, 'offset': 0}
    campaigns = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch campaigns: {response.status_code}")
            break
        data = response.json()
        campaigns.extend(data.get('campaigns', []))
        if len(campaigns) >= data.get('total_items', 0):
            break
        params['offset'] += params['count']
    return campaigns

def fetch_campaign_content(campaign_id):
    url = f"{BASE_URL}/campaigns/{campaign_id}/content"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("html", "")
    else:
        print(f"Failed to fetch content for campaign {campaign_id}. Status: {response.status_code}")
        return ""

def parse_links_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return [a["href"] for a in soup.find_all("a", href=True)]

def fetch_click_details(campaign_id):
    """
    Fetch click performance details for the campaign.
    """
    url = f"{BASE_URL}/reports/{campaign_id}/click-details"
    all_click_details = []
    offset = 0
    while True:
        response = requests.get(url, headers=headers, params={'count': 1000, 'offset': offset})
        if response.status_code != 200:
            print(f"Failed to fetch click details for campaign {campaign_id}. Status: {response.status_code}")
            break
        
        data = response.json()
        click_details = data.get("urls_clicked", [])
        if not click_details:
            break
        
        all_click_details.extend(click_details)
        if len(click_details) < 1000:  # No more pages to retrieve
            break
        offset += 1000
    
    return all_click_details

def normalize_url(url):
    """
    Normalize the URL by lowercasing the scheme and netloc, removing 'www.',
    stripping query parameters except essential ones, and removing any trailing slashes.
    """
    try:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower().lstrip('www.')
        path = parsed.path.rstrip('/')
        
        # Preserve query parameters only if they are critical
        essential_params = ['id', 'utm_source', 'utm_medium', 'utm_campaign']
        query = parse_qs(parsed.query)
        filtered_query = {k: v for k, v in query.items() if k in essential_params}
        query_str = "&".join(f"{k}={v[0]}" for k, v in filtered_query.items() if v)

        # Reconstruct the URL with only essential parameters
        filtered_url = urlunparse((scheme, netloc, path, '', query_str, ''))
        return filtered_url
    except Exception as e:
        print(f"Failed to normalize URL {url}: {e}")
        return url


def should_exclude_link(link):
    try:
        parsed = urlparse(link)
        domain = parsed.netloc.lower().replace("www.", "")
        excluded_domains = {
            "thedp.com",
            "34st.com",
            "underthebutton.com",
            "facebook.com",
            "twitter.com",
            "instagram.com",
            "open.spotify.com",
            "forms.gle",
            "eepurl.com",
            "issuu.com",
            "thedp.revfluent.com",
            "thedp.us2.list-manage.com",
            "upenn.co1.qualtrics.com"
        }
        return domain in excluded_domains
    except Exception:
        return False

def build_click_map_for_campaign(campaign):
    """
    For a given campaign, build a custom click map by:
      1. Extracting the ordered links from the campaign HTML.
      2. Merging with the click details data using improved URL matching.
      3. Skipping any links that are mail-to or that should be excluded.
    """
    campaign_id = campaign.get("id")
    campaign_name = campaign.get("settings", {}).get("title", "N/A")
    print(f"Processing campaign: {campaign_name} ({campaign_id})")
    
    html_content = fetch_campaign_content(campaign_id)
    if not html_content:
        return None

    ordered_links = parse_links_from_html(html_content)
    
    seen = set()
    ordered_links_unique = []
    for link in ordered_links:
        if link.startswith("*|") or link in seen:
            continue
        ordered_links_unique.append(link)
        seen.add(link)
    
    click_details = fetch_click_details(campaign_id)
    click_map_data = {}
    for detail in click_details:
        tracked_url = detail.get("url")
        norm_url = normalize_url(tracked_url)
        click_map_data[norm_url] = detail

    result = []
    order_counter = 0
    for url in ordered_links_unique:
        if url.lower().startswith("mailto:") or should_exclude_link(url):
            continue

        order_counter += 1
        norm_html_url = normalize_url(url)
        detail = click_map_data.get(norm_html_url)
        
        if not detail:
            # Improved Fuzzy Matching Logic
            for tracked_norm, d in click_map_data.items():
                if norm_html_url in tracked_norm or tracked_norm in norm_html_url:
                    detail = d
                    break

        record = {
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "order": order_counter,
            "url": url,
            "total_clicks": detail.get("total_clicks", 0) if detail else 0,
            "unique_clicks": detail.get("unique_clicks", 0) if detail else 0,
            "click_percentage": detail.get("click_percentage", 0) if detail else 0,
            "unique_click_percentage": detail.get("unique_click_percentage", 0) if detail else 0
        }
        result.append(record)
    return result

def build_all_click_maps():
    campaigns = fetch_campaigns()
    all_maps = []
    for campaign in campaigns:
        campaign_name = campaign.get('settings', {}).get('title', '')
        if "DP Daybreak" not in campaign_name:
            continue
        campaign_map = build_click_map_for_campaign(campaign)
        if campaign_map:
            all_maps.extend(campaign_map)
    return all_maps

if __name__ == "__main__":
    all_click_maps = build_all_click_maps()
    
    df = pd.DataFrame(all_click_maps)
    print(df)
    
    output_file = "custom_click_map.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved custom click map data to {output_file}")