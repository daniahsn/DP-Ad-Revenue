import matplotlib.pyplot as plt
import numpy as np

# Data
orders = [1, 2, 3]
total_clicks = [63.0625, 29.91304347826087, 19.382978723404257]
unique_clicks = [53.06875, 22.76086956521739, 11.904255319148936]
click_percentage = [0.02411423639305008, 0.010952620848939151, 0.008040967743475189]
unique_click_percentage = [0.03185023746310338, 0.013758652322314194, 0.008523101947978253]

# Create the figure and primary axis
fig, ax1 = plt.subplots()

# Define bar width and positions
width = 0.35
ind = np.arange(len(orders))

# Plot total and unique clicks as bar charts
bar1 = ax1.bar(ind - width/2, total_clicks, width, label='Total Clicks')
bar2 = ax1.bar(ind + width/2, unique_clicks, width, label='Unique Clicks')
ax1.set_xlabel('Order')
ax1.set_ylabel('Clicks')
ax1.set_xticks(ind)
ax1.set_xticklabels(orders)
ax1.legend(loc='upper left')

# Create a secondary axis for percentages
ax2 = ax1.twinx()
ax2.plot(ind, click_percentage, marker='o', linestyle='-', label='Click Percentage')
ax2.plot(ind, unique_click_percentage, marker='o', linestyle='-', label='Unique Click Percentage')
ax2.set_ylabel('Click Percentage')
ax2.legend(loc='upper right')

# Add a title and display the chart
plt.title('Clicks and Click Percentages by Order')
plt.show()