import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

class AdPerformanceAnalyzer:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)

    def plot_clicks_by_position(self):
        """ Plot total clicks by position with color-coding and trend line. """
        self._plot_clicks('total_clicks', 'Total Clicks', 'Total Clicks vs. Position in Email', 'total_clicks_by_position.png')

    def plot_unique_clicks_by_position(self):
        """ Plot unique clicks by position with color-coding and trend line. """
        self._plot_clicks('unique_clicks', 'Unique Clicks', 'Unique Clicks vs. Position in Email', 'unique_clicks_by_position.png')
        
    def plot_click_percentage_by_position(self):
        """ Plot click percentage by position with color-coding and trend line. """
        self._plot_clicks('click_percentage', 'Click Percentage (%)', 'Click Percentage vs. Position in Email', 'click_percentage_by_position.png')

    def plot_unique_click_percentage_by_position(self):
        """ Plot unique click percentage by position with color-coding and trend line. """
        self._plot_clicks('unique_click_percentage', 'Unique Click Percentage (%)', 'Unique Click Percentage vs. Position in Email', 'unique_click_percentage_by_position.png')

    def _plot_clicks(self, data_column, y_label, title, filename):
        plt.figure(figsize=(14, 7))

        # Plot the scatter plot with color coding based on click values
        click_values = self.df[data_column]
        colors = np.where(click_values > 200, 'red',
                          np.where(click_values > 100, 'orange', 'green'))

        plt.scatter(self.df['order'], click_values, c=colors, alpha=0.6, label='Click Data')

        # Generate trend line using Gaussian smoothing
        unique_orders = np.sort(self.df['order'].unique())
        avg_clicks = [self.df.loc[self.df['order'] == order, data_column].mean() for order in unique_orders]
        smoothed_clicks = gaussian_filter1d(avg_clicks, sigma=2)
        
        plt.plot(unique_orders, smoothed_clicks, color='blue', lw=3, label='Trend Line (Smoothed Average)')

        # Adding labels, title, and legend
        plt.title(title, fontsize=14)
        plt.xlabel('Position in Email (1 = Top, Higher Number = Lower)', fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.legend()
        plt.grid(True)

        # Save the plot and display it
        plt.savefig(filename)
        plt.show()
        plt.close()

    def calculate_order_averages(self, output_csv_path):
        """Calculate averages for specific positions and save to CSV."""
        # Convert 'order' column to numeric, if necessary
        self.df['order'] = pd.to_numeric(self.df['order'], errors='coerce')
        
        # Filter for rows where the order is 1, 2, or 3
        df_filtered = self.df[self.df['order'].isin([1, 2, 3])]
        
        # Group by 'order' and calculate mean for specified columns
        averages = df_filtered.groupby('order')[['total_clicks', 'unique_clicks', 'click_percentage', 'unique_click_percentage']].mean()
        
        # Save results to a new CSV file
        averages.to_csv(output_csv_path)
        print(f"Averages saved to {output_csv_path}")

    # def plot_order_averages(self, input_csv_path, output_image_path):
    #     """Plot and save the order averages visual."""
    #     # Read the averages file
    #     averages = pd.read_csv(input_csv_path)

    #     plt.figure(figsize=(14, 7))

    #     # Plotting the metrics for each order
    #     plt.plot(averages['order'], averages['total_clicks'], marker='o', label='Total Clicks', color='blue')
    #     plt.plot(averages['order'], averages['unique_clicks'], marker='o', label='Unique Clicks', color='orange')
    #     plt.plot(averages['order'], averages['click_percentage'], marker='o', label='Click Percentage', color='green')
    #     plt.plot(averages['order'], averages['unique_click_percentage'], marker='o', label='Unique Click Percentage', color='red')

    #     # Adding labels, title, and legend
    #     plt.title('Order Averages Comparison', fontsize=16)
    #     plt.xlabel('Ad Position (Order)', fontsize=12)
    #     plt.ylabel('Average Values', fontsize=12)
    #     plt.legend()
    #     plt.grid(True)

    #     # Save the plot to a file
    #     plt.savefig(output_image_path)
    #     plt.show()
    #     plt.close()


