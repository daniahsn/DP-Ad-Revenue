"""
Performance analyzer module - responsible for analyzing ad performance data.
"""
import pandas as pd
import numpy as np

class PerformanceAnalyzer:
    def __init__(self, data_source):
        """
        Initialize with data from a CSV file or a pandas DataFrame
        
        Parameters:
        - data_source: Path to CSV file or pandas DataFrame
        """
        if isinstance(data_source, str):
            self.df = pd.read_csv(data_source)
        elif isinstance(data_source, pd.DataFrame):
            self.df = data_source
        else:
            raise TypeError("data_source must be a filepath string or pandas DataFrame")

    def calculate_order_statistics(self, orders=None):
        """
        Calculate statistics for specific ad positions
        
        Parameters:
        - orders: List of orders to analyze (None means all orders)
        
        Returns:
        - DataFrame with statistics for each order
        """
        # Convert 'order' column to numeric, if necessary
        self.df['order'] = pd.to_numeric(self.df['order'], errors='coerce')
        
        # Filter for specific orders if requested
        if orders:
            df_filtered = self.df[self.df['order'].isin(orders)]
        else:
            df_filtered = self.df
        
        # Group by 'order' and calculate statistics
        columns = ['total_clicks', 'unique_clicks', 'click_percentage', 'unique_click_percentage']
        stats = df_filtered.groupby('order')[columns].agg(['mean', 'median', 'std', 'count']).reset_index()
        
        return stats
        
    def get_top_performing_positions(self, metric='total_clicks', top_n=3):
        """
        Get the top performing ad positions
        
        Parameters:
        - metric: Metric to use for ranking ('total_clicks', 'unique_clicks', etc.)
        - top_n: Number of top positions to return
        
        Returns:
        - DataFrame of top positions
        """
        avg_by_position = self.df.groupby('order')[metric].mean().reset_index()
        top_positions = avg_by_position.nlargest(top_n, metric)
        return top_positions
        
    def compare_position_performance(self, orders):
        """
        Compare performance metrics between specified positions
        
        Parameters:
        - orders: List of orders to compare
        
        Returns:
        - DataFrame with performance comparison
        """
        if not isinstance(orders, list) or len(orders) < 2:
            raise ValueError("orders must be a list with at least 2 elements")
            
        filtered_df = self.df[self.df['order'].isin(orders)]
        metrics = ['total_clicks', 'unique_clicks', 'click_percentage', 'unique_click_percentage']
        
        comparison = filtered_df.groupby('order')[metrics].mean().reset_index()
        
        # Calculate relative performance (first position as baseline)
        baseline = comparison.iloc[0]
        for metric in metrics:
            comparison[f'{metric}_relative'] = comparison[metric] / baseline[metric]
            
        return comparison