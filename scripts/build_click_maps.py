"""
Script to build click maps from Mailchimp campaigns.
"""
import os
import pandas as pd
import argparse
from dotenv import load_dotenv

# Add root directory to path so we can import from src
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.campaign_fetcher import CampaignFetcher
from data.click_map_builder import ClickMapBuilder

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Build click maps from Mailchimp campaigns')
    parser.add_argument('--filter', type=str, default=None, 
                        help='Filter campaigns by name (e.g., "DP Daybreak")')
    parser.add_argument('--output', type=str, default='click_map_data.csv',
                        help='Output CSV file path')
    parser.add_argument('--days', type=int, default=365,
                        help='Number of days to look back for campaigns')
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    print(f"Building click maps for campaigns matching filter: {args.filter}")
    print(f"Looking back {args.days} days")
    
    try:
        # Initialize campaign fetcher
        campaign_fetcher = CampaignFetcher()
        
        # Initialize click map builder
        click_map_builder = ClickMapBuilder(campaign_fetcher)
        
        # Build click maps
        click_maps = click_map_builder.build_click_maps(campaign_name_filter=args.filter)
        
        if not click_maps:
            print("No click maps were built. Check your filter criteria.")
            return
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(click_maps)
        df.to_csv(args.output, index=False)
        
        print(f"Successfully built {len(click_maps)} click map records")
        print(f"Data saved to {args.output}")
        
        # Print summary statistics
        print("\nSummary Statistics:")
        print(f"Total campaigns processed: {df['campaign_id'].nunique()}")
        print(f"Average links per campaign: {df.groupby('campaign_id')['order'].count().mean():.2f}")
        print(f"Average total clicks: {df['total_clicks'].mean():.2f}")
        print(f"Average unique clicks: {df['unique_clicks'].mean():.2f}")
        
    except Exception as e:
        print(f"Error building click maps: {e}")

if __name__ == "__main__":
    main()