import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

class AdPerformanceAnalyzer:
    import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

class AdPerformanceAnalyzer:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)

    def plot_clicks_by_position(self):
        """ Plot total clicks by position with color-coding and trend line. """
        self._plot_clicks('total_clicks', 'Total Clicks', 'Total Clicks vs. Position in Email')

    def plot_unique_clicks_by_position(self):
        """ Plot unique clicks by position with color-coding and trend line. """
        self._plot_clicks('unique_clicks', 'Unique Clicks', 'Unique Clicks vs. Position in Email')
        
    def plot_click_percentage_by_position(self):
        """ Plot click percentage by position with color-coding and trend line. """
        self._plot_clicks('click_percentage', 'Click Percentage (%)', 'Click Percentage vs. Position in Email')

    def plot_unique_click_percentage_by_position(self):
        """ Plot unique click percentage by position with color-coding and trend line. """
        self._plot_clicks('unique_click_percentage', 'Unique Click Percentage (%)', 'Unique Click Percentage vs. Position in Email')

    def _plot_clicks(self, data_column, y_label, title):
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
        plt.show()
