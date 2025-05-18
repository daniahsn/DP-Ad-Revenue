"""
Click map builder module - responsible for building click maps from campaign data.
"""
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, parse_qs

class ClickMapBuilder:
    def __init__(self, campaign_fetcher):
        """
        Initialize ClickMapBuilder with a campaign fetcher
        
        Parameters:
        - campaign_fetcher: Instance of CampaignFetcher class
        """
        self.campaign_fetcher = campaign_fetcher
        self.excluded_domains = {
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

    def parse_links_from_html(self, html):
        """
        Extract all links from HTML content
        
        Parameters:
        - html: HTML content as string
        
        Returns:
        - List of URLs as strings
        """
        soup = BeautifulSoup(html, "html.parser")
        return [a["href"] for a in soup.find_all("a", href=True)]

    def normalize_url(self, url):
        """
        Normalize the URL by lowercasing the scheme and netloc, removing 'www.',
        stripping query parameters except essential ones, and removing trailing slashes.
        
        Parameters:
        - url: URL to normalize
        
        Returns:
        - Normalized URL as string
        """
        try:
            parsed = urlparse(url)
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower().lstrip('www.')
            path = parsed.path.rstrip('/')
            
            # Preserve only essential query parameters
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

    def should_exclude_link(self, link):
        """
        Check if a link should be excluded based on domain
        
        Parameters:
        - link: URL to check
        
        Returns:
        - Boolean indicating whether the link should be excluded
        """
        try:
            parsed = urlparse(link)
            domain = parsed.netloc.lower().replace("www.", "")
            return domain in self.excluded_domains
        except Exception:
            return False

    def build_click_map_for_campaign(self, campaign):
        """
        For a given campaign, build a custom click map by:
          1. Extracting the ordered links from the campaign HTML.
          2. Merging with the click details data using improved URL matching.
          3. Skipping any links that are mail-to or that should be excluded.
          
        Parameters:
        - campaign: Campaign dictionary
        
        Returns:
        - List of click map records
        """
        campaign_id = campaign.get("id")
        campaign_name = campaign.get("settings", {}).get("title", "N/A")
        print(f"Processing campaign: {campaign_name} ({campaign_id})")
        
        html_content = self.campaign_fetcher.fetch_campaign_content(campaign_id)
        if not html_content:
            return None

        ordered_links = self.parse_links_from_html(html_content)
        
        # Get unique links while preserving order
        seen = set()
        ordered_links_unique = []
        for link in ordered_links:
            if link.startswith("*|") or link in seen:
                continue
            ordered_links_unique.append(link)
            seen.add(link)
        
        click_details = self.campaign_fetcher.fetch_click_details(campaign_id)
        click_map_data = {}
        for detail in click_details:
            tracked_url = detail.get("url")
            norm_url = self.normalize_url(tracked_url)
            click_map_data[norm_url] = detail

        result = []
        order_counter = 0
        for url in ordered_links_unique:
            if url.lower().startswith("mailto:") or self.should_exclude_link(url):
                continue

            order_counter += 1
            norm_html_url = self.normalize_url(url)
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

    def build_click_maps(self, campaigns=None, campaign_name_filter=None):
        """
        Build click maps for multiple campaigns
        
        Parameters:
        - campaigns: List of campaign dictionaries (if None, will fetch campaigns)
        - campaign_name_filter: String to filter campaign names (e.g., "DP Daybreak")
        
        Returns:
        - List of click map records for all campaigns
        """
        if not campaigns:
            # Create a filter function based on the name filter
            def filter_func(campaign):
                if not campaign_name_filter:
                    return True
                campaign_name = campaign.get('settings', {}).get('title', '')
                return campaign_name_filter in campaign_name
            
            campaigns = self.campaign_fetcher.fetch_campaigns(campaign_filter=filter_func)
        
        all_maps = []
        for campaign in campaigns:
            campaign_map = self.build_click_map_for_campaign(campaign)
            if campaign_map:
                all_maps.extend(campaign_map)
        
        return all_maps