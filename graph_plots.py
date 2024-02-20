## IDEAS 

# focus on plotting average edge weight against c for now 
# essentially c takes 4 values [0,01, 0.03, 0.1, 0.3] 
# for each value we need to get the average edge weight 
# i.e. say the following {0.1 : list of all average edge weight , so on}
# then we can plot this using pandas and dataframes (looking online)

import csv 
import pandas as pd
import matplotlib.pyplot as plt


data = pd.read_csv("statistics.csv") # turns csv file of data to a dataframe


tempdict = {'0.01' : [] , '0.03' : [] , '0.1' : [] , '0.3' : []} # experiment basis , for now stores {value of c: list of average edge weights corresponding to this value}
for index, row in data.iterrows(): # for each datapoint add the edge weight to the corresponding key in the dictionary
    tempdict[str(row['c'])].append(row['avg_edw']) 

# {0.01 : [a, b, c, d, e] , 0.1 : [x, y ,z]}





for key, values in tempdict.items():
    print(key)
    x = [str(key)] * len(values) # Repeat the key for each value
    y = values
    plt.plot(x, y, marker='o', markersize=5)  # Plot vertical lines

plt.xlabel('c')
plt.ylabel('Average edge weight')
#plt.xticks([0.01, 0.03, 0.1, 0.3])

# Show the plot
plt.show()
