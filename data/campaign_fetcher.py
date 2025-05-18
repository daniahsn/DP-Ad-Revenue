"""
Campaign fetcher module - responsible for retrieving campaign data from Mailchimp API.
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

class CampaignFetcher:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.API_KEY = os.getenv("API_KEY")
        self.SERVER = os.getenv("SERVER")
        
        if not self.API_KEY or not self.SERVER:
            raise ValueError("❌ Missing API_KEY or SERVER. Please check your .env file.")
            
        self.BASE_URL = f"https://{self.SERVER}.api.mailchimp.com/3.0"
        self.headers = {"Authorization": f"Bearer {self.API_KEY}"}

    def fetch_campaigns(self, days_back=365, campaign_filter=None):
        """
        Fetch campaigns from Mailchimp API
        
        Parameters:
        - days_back: Number of days to look back for campaigns
        - campaign_filter: Filter function to apply to campaign results
        
        Returns:
        - List of campaign dictionaries
        """
        since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%S')
        url = f'{self.BASE_URL}/campaigns'
        params = {'since_send_time': since_date, 'count': 100, 'offset': 0}
        campaigns = []
        
        while True:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code != 200:
                print(f"Failed to fetch campaigns: {response.status_code}")
                break
                
            data = response.json()
            fetched_campaigns = data.get('campaigns', [])
            
            # Apply filter if provided
            if campaign_filter:
                fetched_campaigns = [c for c in fetched_campaigns if campaign_filter(c)]
                
            campaigns.extend(fetched_campaigns)
            
            if len(campaigns) >= data.get('total_items', 0) or not fetched_campaigns:
                break
                
            params['offset'] += params['count']
            
        return campaigns

    def fetch_campaign_content(self, campaign_id):
        """
        Fetch HTML content for a specific campaign
        
        Parameters:
        - campaign_id: ID of the campaign
        
        Returns:
        - HTML content as string
        """
        url = f"{self.BASE_URL}/campaigns/{campaign_id}/content"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("html", "")
        else:
            print(f"Failed to fetch content for campaign {campaign_id}. Status: {response.status_code}")
            return ""

    def fetch_click_details(self, campaign_id):
        """
        Fetch click performance details for a campaign
        
        Parameters:
        - campaign_id: ID of the campaign
        
        Returns:
        - List of click detail dictionaries
        """
        url = f"{self.BASE_URL}/reports/{campaign_id}/click-details"
        all_click_details = []
        offset = 0
        
        while True:
            response = requests.get(url, headers=self.headers, params={'count': 1000, 'offset': offset})
            
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