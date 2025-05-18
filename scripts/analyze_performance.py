"""
Script to analyze ad performance from click map data.
"""
import os
import pandas as pd
import argparse

# Add root directory to path so we can import from src
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.performance_analyzer import PerformanceAnalyzer
from visualization.plot_generator import PlotGenerator
from visualization.chart_creator import ChartCreator

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze ad performance from click map data')
    parser.add_argument('--input', type=str, default='click_map_data.csv',
                        help='Input CSV file with click map data')
    parser.add_argument('--output-dir', type=str, default='outputs',
                        help='Directory to save analysis outputs')
    parser.add_argument('--top-positions', type=int, default=3,
                        help='Number of top positions to analyze')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    print(f"Analyzing ad performance from {args.input}")
    
    try:
        # Load click map data
        data = pd.read_csv(args.input)
        
        # Initialize performance analyzer
        analyzer = PerformanceAnalyzer(data)
        
        # Calculate statistics for top positions
        top_positions = list(range(1, args.top_positions + 1))
        top_stats = analyzer.calculate_order_statistics(top_positions)
        
        # Save statistics to CSV
        top_stats_file = os.path.join(args.output_dir, 'top_positions_stats.csv')
        top_stats.to_csv(top_stats_file)
        print(f"Top positions statistics saved to {top_stats_file}")
        
        # Compare position performance
        comparison = analyzer.compare_position_performance(top_positions)
        comparison_file = os.path.join(args.output_dir, 'position_comparison.csv')
        comparison.to_csv(comparison_file)
        print(f"Position comparison saved to {comparison_file}")
        
        # Initialize visualization tools
        plot_generator = PlotGenerator(data, args.output_dir)
        chart_creator = ChartCreator(args.output_dir)
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        
        # Generate scatter plots with trend lines
        plot_generator.plot_metric_by_position(
            'total_clicks', 
            'Total Clicks vs. Position in Email', 
            'Total Clicks', 
            'total_clicks_by_position.png'
        )
        
        plot_generator.plot_metric_by_position(
            'unique_clicks', 
            'Unique Clicks vs. Position in Email', 
            'Unique Clicks', 
            'unique_clicks_by_position.png'
        )
        
        plot_generator.plot_metric_by_position(
            'click_percentage', 
            'Click Percentage vs. Position in Email', 
            'Click Percentage (%)', 
            'click_percentage_by_position.png'
        )
        
        plot_generator.plot_metric_by_position(
            'unique_click_percentage', 
            'Unique Click Percentage vs. Position in Email', 
            'Unique Click Percentage (%)', 
            'unique_click_percentage_by_position.png'
        )
        
        # Generate position comparison chart
        chart_creator.create_position_comparison_bar(
            comparison,
            "Ad Performance by Position",
            "position_comparison_bar.png"
        )
        
        # Generate heatmap
        chart_creator.create_position_heatmap(
            data,
            title="Ad Performance Heatmap by Position",
            filename="position_heatmap.png"
        )
        
        # Generate trend charts for each metric
        metrics = ['total_clicks', 'unique_clicks', 'click_percentage', 'unique_click_percentage']
        for metric in metrics:
            chart_creator.create_performance_trend(
                data, 
                metric=metric,
                filename=f"{metric}_trend.png"
            )
        
        print(f"All visualizations saved to {args.output_dir}")
        
        # Print summary insights
        top_performer = analyzer.get_top_performing_positions(metric='total_clicks', top_n=1)
        top_position = top_performer.iloc[0]['order']
        top_clicks = top_performer.iloc[0]['total_clicks']
        
        print("\nKey Insights:")
        print(f"Position {top_position} performs best with an average of {top_clicks:.2f} total clicks")
        
        # Performance drop from position 1 to 2
        if 1 in comparison['order'].values and 2 in comparison['order'].values:
            pos1 = comparison[comparison['order'] == 1]
            pos2 = comparison[comparison['order'] == 2]
            drop_percentage = (1 - pos2['total_clicks'].values[0] / pos1['total_clicks'].values[0]) * 100
            print(f"Performance drops {drop_percentage:.2f}% from position 1 to position 2")
        
    except Exception as e:
        print(f"Error analyzing ad performance: {e}")

if __name__ == "__main__":
    main()