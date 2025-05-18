"""
Plot generator module - responsible for creating visualizations of ad performance data.
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

class PlotGenerator:
    def __init__(self, data, output_dir=None):
        """
        Initialize with data and optional output directory
        
        Parameters:
        - data: pandas DataFrame with ad performance data
        - output_dir: Directory to save plots (if None, plots are only displayed)
        """
        self.data = data
        self.output_dir = output_dir
        
    def save_or_show(self, plt, filename=None):
        """
        Save plot to file if output_dir is set, otherwise just show it
        
        Parameters:
        - plt: Matplotlib pyplot instance
        - filename: Name of file to save (if None, uses a default name)
        """
        if self.output_dir and filename:
            import os
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            full_path = os.path.join(self.output_dir, filename)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {full_path}")
        
        plt.show()
        plt.close()

    def plot_metric_by_position(self, metric, title, ylabel, filename=None):
        """
        Plot a metric by ad position with color-coding and trend line
        
        Parameters:
        - metric: Column name in data to plot
        - title: Title for the plot
        - ylabel: Label for y-axis
        - filename: Name of file to save
        """
        plt.figure(figsize=(14, 7))

        # Plot the scatter plot with color coding based on click values
        values = self.data[metric]
        
        # Determine color thresholds dynamically
        high_threshold = values.quantile(0.75)
        med_threshold = values.quantile(0.5)
        
        colors = np.where(values > high_threshold, 'red',
                          np.where(values > med_threshold, 'orange', 'green'))

        plt.scatter(self.data['order'], values, c=colors, alpha=0.6, label='Data Points')

        # Generate trend line using Gaussian smoothing
        unique_orders = np.sort(self.data['order'].unique())
        avg_values = [self.data.loc[self.data['order'] == order, metric].mean() for order in unique_orders]
        smoothed_values = gaussian_filter1d(avg_values, sigma=2)
        
        plt.plot(unique_orders, smoothed_values, color='blue', lw=3, label='Trend Line (Smoothed Average)')

        # Adding labels, title, and legend
        plt.title(title, fontsize=14)
        plt.xlabel('Position in Email (1 = Top, Higher Number = Lower)', fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.legend()
        plt.grid(True)

        # Save or show the plot
        self.save_or_show(plt, filename)

    def plot_position_comparison(self, comparison_data, title="Position Comparison", filename=None):
        """
        Create a bar chart comparing different metrics across positions
        
        Parameters:
        - comparison_data: DataFrame with position comparison data
        - title: Title for the plot
        - filename: Name of file to save
        """
        fig, ax1 = plt.subplots(figsize=(12, 8))

        # Set up position for bars
        positions = comparison_data['order'].values
        x = np.arange(len(positions))
        width = 0.35

        # Plot total and unique clicks as bar charts
        bar1 = ax1.bar(x - width/2, comparison_data['total_clicks'], width, label='Total Clicks')
        bar2 = ax1.bar(x + width/2, comparison_data['unique_clicks'], width, label='Unique Clicks')
        ax1.set_xlabel('Position in Email')
        ax1.set_ylabel('Clicks')
        ax1.set_xticks(x)
        ax1.set_xticklabels(positions)
        ax1.legend(loc='upper left')

        # Create a secondary axis for percentages
        ax2 = ax1.twinx()
        ax2.plot(x, comparison_data['click_percentage'], marker='o', linestyle='-', 
                color='green', label='Click Percentage')
        ax2.plot(x, comparison_data['unique_click_percentage'], marker='s', linestyle='-', 
                color='purple', label='Unique Click Percentage')
        ax2.set_ylabel('Click Percentage')
        ax2.legend(loc='upper right')

        plt.title(title, fontsize=16)
        plt.tight_layout()
        
        # Save or show the plot
        self.save_or_show(plt, filename)
        
    def create_heatmap(self, title="Click Heatmap by Position", filename=None):
        """
        Create a heatmap showing click performance across positions
        
        Parameters:
        - title: Title for the plot
        - filename: Name of file to save
        """
        import seaborn as sns
        
        # Pivot the data to create a position-based heatmap
        pivot_data = self.data.pivot_table(
            index='order', 
            values=['total_clicks', 'unique_clicks', 'click_percentage', 'unique_click_percentage'],
            aggfunc='mean'
        ).head(10)  # Limit to first 10 positions
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(pivot_data, annot=True, cmap="YlGnBu", fmt=".2f")
        plt.title(title, fontsize=16)
        plt.tight_layout()
        
        # Save or show the plot
        self.save_or_show(plt, filename)
        