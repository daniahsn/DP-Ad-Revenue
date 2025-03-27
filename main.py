import pandas as pd   # For data manipulation and analysis
import matplotlib.pyplot as plt  # For generating visualizations (graphs, charts, etc.)

from ad_performance_analyzer import AdPerformanceAnalyzer
from campaign_clickmap_builder import CampaignClickMapBuilder

builder = CampaignClickMapBuilder()
print("Building click maps for all campaigns...")
    
    # Build click maps for all campaigns
all_click_maps = builder.build_all_click_maps()

# Create a DataFrame from the results and save to CSV
df = pd.DataFrame(all_click_maps)
print(df)

output_file = "custom_click_map.csv"
df.to_csv(output_file, index=False)
print(f"Saved custom click map data to {output_file}")


analyzer = AdPerformanceAnalyzer("custom_click_map.csv")

# Generate all four graphs
analyzer.plot_clicks_by_position()
analyzer.plot_unique_clicks_by_position()
analyzer.plot_click_percentage_by_position()
analyzer.plot_unique_click_percentage_by_position()

analyzer.calculate_order_averages("order_averages.csv")
print("Order averages calculated and saved to order_averages.csv")

analyzer.plot_order_averages("order_averages.csv", "order_averages_visual.png")