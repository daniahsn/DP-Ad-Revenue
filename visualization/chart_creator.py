"""
Chart creator module - responsible for creating specialized charts for ad performance analysis.
Complements the PlotGenerator class by offering additional visualization types.
"""
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.ticker import PercentFormatter
import pandas as pd
from datetime import datetime, timedelta

class ChartCreator:
    def __init__(self, data, output_dir=None):
        """
        Initialize with data and optional output directory
        
        Parameters:
        - data: pandas DataFrame with ad performance data
        - output_dir: Directory to save charts (if None, charts are only displayed)
        """
        self.data = data
        self.output_dir = output_dir
        
    def save_or_show(self, plt, filename=None):
        """
        Save chart to file if output_dir is set, otherwise just show it
        
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
            print(f"Chart saved to {full_path}")
        
        plt.show()
        plt.close()

    def create_performance_radar(self, positions=None, metrics=None, filename=None):
        """
        Create a radar chart (spider chart) to visualize multiple metrics across different positions
        
        Parameters:
        - positions: List of positions to include (defaults to top 5)
        - metrics: List of metrics to include (defaults to standard engagement metrics)
        - filename: Name of file to save
        """
        if positions is None:
            positions = sorted(self.data['order'].unique())[:5]  # Default to top 5 positions
            
        if metrics is None:
            metrics = ['click_percentage', 'unique_click_percentage', 'impression_rate', 'engagement_score']
            
        # Filter data for specified positions and metrics
        filtered_data = self.data[self.data['order'].isin(positions)]
        
        # Create a pivot table with positions as rows and metrics as columns
        pivot_data = filtered_data.pivot_table(index='order', values=metrics)
        
        # Normalize data to 0-1 scale for radar chart
        normalized_data = pivot_data.copy()
        for metric in metrics:
            if metric in pivot_data.columns:
                max_val = pivot_data[metric].max()
                min_val = pivot_data[metric].min()
                if max_val > min_val:  # Avoid division by zero
                    normalized_data[metric] = (pivot_data[metric] - min_val) / (max_val - min_val)
        
        # Set up the radar chart
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, polar=True)
        
        # Set the angles for each metric
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # Close the loop
        
        # Plot each position as a separate line
        for position in positions:
            if position in normalized_data.index:
                values = normalized_data.loc[position].values.flatten().tolist()
                values += values[:1]  # Close the loop
                ax.plot(angles, values, linewidth=2, label=f"Position {position}")
                ax.fill(angles, values, alpha=0.1)
        
        # Set labels and styling
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([m.replace('_', ' ').title() for m in metrics])
        ax.set_yticklabels([])  # Hide radial labels
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.title("Ad Performance Metrics by Position", size=15)
        
        self.save_or_show(plt, filename)

    def create_funnel_chart(self, steps=None, normalize=True, filename=None):
        """
        Create a funnel chart showing conversion at each step of the ad funnel
        
        Parameters:
        - steps: List of column names representing funnel steps (in order)
        - normalize: Whether to show percentages relative to first step
        - filename: Name of file to save
        """
        if steps is None:
            steps = ['impressions', 'views', 'clicks', 'unique_clicks', 'conversions']
        
        # Aggregate the data for each step
        funnel_data = []
        for step in steps:
            if step in self.data.columns:
                funnel_data.append(self.data[step].sum())
            else:
                print(f"Warning: {step} not found in data, using NaN")
                funnel_data.append(np.nan)
        
        # Create the funnel chart
        plt.figure(figsize=(12, 8))
        
        # Calculate percentages if requested
        if normalize:
            percentages = [100.0] + [100 * funnel_data[i] / funnel_data[0] 
                                    for i in range(1, len(funnel_data))]
        else:
            percentages = [100 * val / max(funnel_data) for val in funnel_data]
        
        # Generate colors - from dark to light blue
        colors = plt.cm.Blues(np.linspace(0.8, 0.3, len(steps)))
        
        # Create bars with decreasing widths
        y_pos = np.arange(len(steps))
        width_factors = np.linspace(1.0, 0.5, len(steps))
        
        for i, (width_factor, val, color) in enumerate(zip(width_factors, funnel_data, colors)):
            bar_width = 0.8 * width_factor
            bar_center = (1 - width_factor) / 2
            plt.barh(y_pos[i], percentages[i], color=color, height=bar_width, 
                    left=bar_center * (100 - percentages[i]))
            
            # Add data labels
            plt.text(percentages[i] + 2, y_pos[i], f"{val:,.0f} ({percentages[i]:.1f}%)", 
                    va='center', ha='left' if percentages[i] < 50 else 'right',
                    color='black' if percentages[i] < 85 else 'white')
        
        plt.yticks(y_pos, [s.replace('_', ' ').title() for s in steps])
        plt.xlabel('Percentage')
        plt.gca().xaxis.set_major_formatter(PercentFormatter())
        plt.title('Ad Performance Funnel', fontsize=16)
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        self.save_or_show(plt, filename)
        
    def create_time_series(self, metric, time_col='date', window=7, filename=None):
        """
        Create a time series chart with moving average for a specific metric
        
        Parameters:
        - metric: Column name of the metric to visualize
        - time_col: Column containing time/date information
        - window: Window size for moving average
        - filename: Name of file to save
        """
        if time_col not in self.data.columns or metric not in self.data.columns:
            print(f"Error: Required columns not found: {time_col} or {metric}")
            return
            
        # Ensure data is properly sorted by time
        time_series_data = self.data.sort_values(by=time_col)
        
        # Group by date and calculate mean of the metric
        if pd.api.types.is_datetime64_any_dtype(time_series_data[time_col]):
            daily_data = time_series_data.groupby(time_series_data[time_col].dt.date)[metric].mean().reset_index()
        else:
            daily_data = time_series_data.groupby(time_col)[metric].mean().reset_index()
        
        # Calculate moving average
        daily_data['moving_avg'] = daily_data[metric].rolling(window=window, min_periods=1).mean()
        
        # Create the plot
        plt.figure(figsize=(14, 7))
        plt.plot(daily_data[time_col], daily_data[metric], marker='o', alpha=0.6, 
                linestyle='-', label=f"{metric.replace('_', ' ').title()}")
        plt.plot(daily_data[time_col], daily_data['moving_avg'], 'r-', 
                linewidth=3, label=f"{window}-Day Moving Average")
        
        plt.title(f"Time Series of {metric.replace('_', ' ').title()}", fontsize=16)
        plt.xlabel("Date")
        plt.ylabel(metric.replace('_', ' ').title())
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Rotate x-axis labels if they are dates
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        self.save_or_show(plt, filename)
        
    def create_position_efficiency_chart(self, filename=None):
        """
        Create a chart showing efficiency (clicks per impression) by position
        
        Parameters:
        - filename: Name of file to save
        """
        # Calculate efficiency metrics if they don't exist
        if 'efficiency' not in self.data.columns and 'impressions' in self.data.columns:
            self.data['efficiency'] = self.data['total_clicks'] / self.data['impressions'].replace(0, np.nan)
        
        # Group by position and calculate mean efficiency
        position_data = self.data.groupby('order')['efficiency'].mean().reset_index()
        position_data = position_data.sort_values('order')
        
        # Create the chart
        plt.figure(figsize=(12, 6))
        
        # Create bars with color gradient based on efficiency
        bars = plt.bar(position_data['order'], position_data['efficiency'], 
                     color=plt.cm.viridis(position_data['efficiency'] / position_data['efficiency'].max()))
        
        # Add trend line
        z = np.polyfit(position_data['order'], position_data['efficiency'], 2)
        p = np.poly1d(z)
        x_trend = np.linspace(position_data['order'].min(), position_data['order'].max(), 100)
        plt.plot(x_trend, p(x_trend), 'r--', alpha=0.7, label='Trend (Polynomial Fit)')
        
        plt.xlabel('Position in Email')
        plt.ylabel('Efficiency (Clicks per Impression)')
        plt.title('Ad Efficiency by Position', fontsize=16)
        plt.grid(axis='y', alpha=0.3)
        plt.legend()
        
        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                   f'{height:.3f}', ha='center', va='bottom', rotation=0)
        
        self.save_or_show(plt, filename)
    
    def create_comparative_heatmap(self, segment_col, metric, filename=None):
        """
        Create a heatmap comparing a metric across different positions and segments
        
        Parameters:
        - segment_col: Column to use for segmentation (e.g., 'campaign', 'audience')
        - metric: Metric to visualize in the heatmap
        - filename: Name of file to save
        """
        if segment_col not in self.data.columns or 'order' not in self.data.columns:
            print(f"Error: Required columns not found")
            return
            
        # Create pivot table: positions as rows, segments as columns, metric as values
        pivot_data = self.data.pivot_table(
            index='order', 
            columns=segment_col,
            values=metric,
            aggfunc='mean'
        ).fillna(0)
        
        # Create the heatmap
        plt.figure(figsize=(14, 10))
        ax = sns.heatmap(pivot_data, annot=True, cmap="YlGnBu", fmt=".2f", 
                         linewidths=.5, cbar_kws={'label': metric.replace('_', ' ').title()})
        
        plt.title(f'{metric.replace("_", " ").title()} by Position and {segment_col.title()}', fontsize=16)
        plt.tight_layout()
        
        self.save_or_show(plt, filename)

    def create_engagement_distribution(self, metric='total_clicks', by_position=True, filename=None):
        """
        Create a distribution plot (histogram + KDE) for engagement metrics
        
        Parameters:
        - metric: The engagement metric to visualize
        - by_position: Whether to show distribution by position
        - filename: Name of file to save
        """
        plt.figure(figsize=(12, 7))
        
        if by_position:
            # Get top positions by frequency
            top_positions = self.data['order'].value_counts().nlargest(5).index.tolist()
            position_data = self.data[self.data['order'].isin(top_positions)]
            
            # Create distribution plot for each position
            for position in top_positions:
                subset = position_data[position_data['order'] == position]
                sns.kdeplot(subset[metric], label=f'Position {position}', fill=True, alpha=0.3)
                
            plt.title(f'Distribution of {metric.replace("_", " ").title()} by Position', fontsize=16)
        else:
            # Create an overall distribution
            sns.histplot(self.data[metric], kde=True, color='skyblue')
            plt.title(f'Distribution of {metric.replace("_", " ").title()}', fontsize=16)
        
        plt.xlabel(metric.replace('_', ' ').title())
        plt.ylabel('Density')
        if by_position:
            plt.legend()
        plt.grid(True, alpha=0.3)
        
        self.save_or_show(plt, filename)