import os            # For interacting with your operating system (e.g., file paths)
import sys           # For system-specific parameters and functions
import time          # For handling time-related functions (e.g., sleep, measuring execution time)
import random        # For generating random numbers (if needed)
import json          # For reading and writing JSON files (if needed)
import pandas as pd   # For data manipulation and analysis
import matplotlib.pyplot as plt  # For generating visualizations (graphs, charts, etc.)

# Ensure plots are displayed properly
plt.style.use('seaborn')

# Check if the 'data' folder exists
if not os.path.exists('data'):
    os.makedirs('data')
