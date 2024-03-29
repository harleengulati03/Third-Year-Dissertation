import pandas as pd
import matplotlib.pyplot as plt
data = pd.read_csv("statistics.csv") # turns csv file of data to a dataframe

params = ["c", "h", "a", "theta_h", "theta_a"] 
outcomes = ["average edge weight", "number of communites", "modularity", "range of avg comm. states", "std. of avg comm.states"]
ycount = 0
fig, axs = plt.subplots(5,5, figsize=(15,15))
for outcome in outcomes:
    xcount = 0
    for param in params:
        dict_outcomes = {'0.01' : [] , '0.03' : [] , '0.1' : [] , '0.3' : []}
        for index, row in data.iterrows():
            dict_outcomes[str(row[param])].append(row[outcome])
        for key, values in dict_outcomes.items():
            x = [str(key)] * len(values) # Repeat the key for each value
            y = values 
            axs[ycount, xcount].plot(x, y, marker='o', markersize=10, color="blue", alpha=0.01)

        xcount += 1
    ycount+=1

count_param = 0
count_outcomes = 0
'''for ax in axs.flat:
    if count_param == len(params):
        count_outcomes += 1
        count_param = 0
    ax.set(xlabel=params[count_param], ylabel=outcomes[count_outcomes])
    count_param += 1'''

for ax in axs[-1, :]:
    ax.set_xlabel(params[count_param])
    count_param +=1

# Set y labels only for the first column
for ax in axs[:, 0]:
    ax.set_ylabel(outcomes[count_outcomes])
    count_outcomes += 1


# Hide x labels and tick labels for top plots and y ticks for right plots.
'''for ax in axs.flat:
    ax.label_outer()'''

plt.tight_layout()
plt.show()


'''tempdict = {'0.01' : [] , '0.03' : [] , '0.1' : [] , '0.3' : []} # experiment basis , for now stores {value of c: list of average edge weights corresponding to this value}
for index, row in data.iterrows(): # for each datapoint add the edge weight to the corresponding key in the dictionary
    tempdict[str(row[param])].append(row[outcome]) 

# {0.01 : [a, b, c, d, e] , 0.1 : [x, y ,z]}





for key, values in tempdict.items():
    print(key)
    x = [str(key)] * len(values) # Repeat the key for each value
    y = values
    plt.plot(x, y, marker='o', markersize=10, color="blue", alpha=0.1)  # Plot vertical lines

plt.xlabel('c')
plt.ylabel('Average edge weight')
#plt.xticks([0.01, 0.03, 0.1, 0.3])

# Show the plot
plt.show()'''
