import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file into a DataFrame
df = pd.read_csv('Profit.csv')

# plot the graph of price column
df.plot(x='timestamp', y='profit', kind='line')
plt.show()
