import os            # For interacting with your operating system (e.g., file paths)
import sys           # For system-specific parameters and functions
import time          # For handling time-related functions (e.g., sleep, measuring execution time)
import random        # For generating random numbers (if needed)
import json          # For reading and writing JSON files (if needed)
import pandas as pd   # For data manipulation and analysis
import matplotlib.pyplot as plt  # For generating visualizations (graphs, charts, etc.)

from ad_performance_analyzer import AdPerformanceAnalyzer

analyzer = AdPerformanceAnalyzer("custom_click_map.csv")

# Generate all four graphs
analyzer.plot_clicks_by_position()
analyzer.plot_unique_clicks_by_position()
analyzer.plot_click_percentage_by_position()
analyzer.plot_unique_click_percentage_by_position()