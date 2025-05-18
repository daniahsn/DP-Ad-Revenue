# 📬 Mailchimp Ad Analytics

A modular Python toolkit for analyzing ad performance in Mailchimp campaigns. This tool helps you understand how link position affects click rates in email newsletters.

---

## 📋 Features

- **Data Collection**: Fetch campaign data from Mailchimp API and build customized click maps  
- **Performance Analysis**: Calculate detailed statistics on ad performance by position  
- **Visualization**: Generate insightful charts and graphs to understand click patterns  
- **Modular Design**: Cleanly separated components make it easy to extend and maintain  

---

## 🏗️ Project Structure

```
mailchimp_ad_analytics/
│
├── src/
│   ├── data/
│   │   ├── campaign_fetcher.py      # Responsible for fetching campaign data
│   │   └── click_map_builder.py     # Builds click maps from campaign data
│   │
│   ├── analysis/
│   │   └── performance_analyzer.py  # Analyzes click data
│   │
│   └── visualization/
│       ├── plot_generator.py        # General plotting utilities
│       └── chart_creator.py         # Creates specific chart types
│
├── scripts/
│   ├── build_click_maps.py          # Script to build click maps only
│   ├── analyze_performance.py       # Script to analyze performance only
│   └── run_full_pipeline.py         # Script that runs the entire pipeline
│
├── .env.example                     # Template for environment variables
├── requirements.txt                 # Project dependencies
└── README.md                        # Project documentation
```

---

## 🚀 Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/mailchimp-ad-analytics.git
cd mailchimp-ad-analytics
```

Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Set up your Mailchimp API credentials:

```bash
cp .env.example .env
```

Then edit the `.env` file with your Mailchimp API key and server prefix.

---

## 🔧 Usage

### Running the Full Pipeline

To run the complete analysis pipeline (fetch data, analyze, and visualize):

```bash
python scripts/run_full_pipeline.py --filter "DP Daybreak" --output-dir outputs
```

**Options:**

- `--filter`: Filter campaigns by name (e.g., "DP Daybreak")  
- `--days`: Number of days to look back for campaigns (default: 365)  
- `--output-dir`: Directory to save analysis outputs (default: outputs)  
- `--top-positions`: Number of top positions to analyze (default: 3)  
- `--skip-fetch`: Skip fetching data and use existing click map data  
- `--input-file`: Input CSV file if skipping fetch (default: `click_map_data.csv`)  

---

## 📊 Understanding the Results

### Data Files

- `click_map_data.csv`: Raw data of clicks organized by position in email  
- `top_positions_stats.csv`: Statistics for the top ad positions  
- `position_comparison.csv`: Direct comparison of different position metrics  

### Visualizations

- **Position Scatter Plots**: Shows clicks/percentages by position with trend lines  
- **Position Comparison Bar**: Compare metrics across different positions  
- **Performance Heatmap**: Visualize all metrics by position in a heatmap  
- **Trend Charts**: Line charts showing performance trends for different metrics  

### Key Insights

- Which position performs best for total clicks and unique clicks  
- The percentage drop in performance between positions  
- Patterns in click behavior based on position  

---

## 🧩 Modular Components

The codebase is designed with clean separation of concerns:

### Data Layer

- `CampaignFetcher`: Handles all API interactions with Mailchimp  
- `ClickMapBuilder`: Processes campaign data into structured click maps  

### Analysis Layer

- `PerformanceAnalyzer`: Provides statistical analysis of ad performance  

### Visualization Layer

- `PlotGenerator`: Creates general-purpose visualizations  
- `ChartCreator`: Builds specialized charts for ad analysis  

