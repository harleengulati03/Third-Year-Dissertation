import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data_1dim = pd.read_csv("Sayama Replication/statistics.csv")
data_2dim = pd.read_csv("MAX_MIN/max_min.csv")

params = ["c", "h", "a", "theta_h", "theta_a"] 
outcomes = ["average edge weight"]

param_vals = ["0.01", "0.03", "0.1", "0.3"]
fig, axs = plt.subplots()


for outcome in outcomes:

    for param in params: 
        dict_1dim_outcomes = {"0.01" : [] , "0.03" : [] , "0.1" : [] , "0.3" : []}
        dict_2dim_outcomes = {"0.01" : [] , "0.03" : [] , "0.1" : [] , "0.3" : []}

        for index, row in data_1dim.iterrows():
            dict_1dim_outcomes[str(row[param])].append(row[outcome])
        
        for index, row in data_2dim.iterrows():
            dict_2dim_outcomes[str(row[param])].append(row[outcome])

        for val in param_vals:
            y_1dim = dict_1dim_outcomes[str(val)]
            x_1dim = [str(val)] * len(y_1dim)

            y_2dim = dict_2dim_outcomes[str(val)]
            x_2dim = [str(val)] * len(y_2dim)
            offset = 0.005 * 0.005 * 0.005 * 0.005 * 0.005 * 0.005 * 0.005
            x2_offset = [str(float(x) + offset) for x in x_2dim]

            x_2dim = np.array(x_2dim)
            

            axs.plot(x_1dim, y_1dim, marker='o', markersize=10, color="blue", alpha=0.01)

            axs.plot(x2_offset, y_2dim, marker='o', markersize=10, color="green", alpha=0.01)
        axs.xaxis.set_ticks(["0.01", "0.03", "0.1", "0.3"])

        #axs.xaxis.set_ticks(range(len([0.01, 0.03, 0.1, 0.3])))
        #axs.xaxis.set_ticklabels([0.01, 0.03, 0.1, 0.3])
        #axs.xaxis.set_ticklabels(x)
        #axs[ycount,xcount].set(xticks = [0.01, 0.03, 0.1, 0.5], xticklabels=['0.01', '0.03', '0.1', '0.3'])

count_param = 0
count_outcomes = 0

# for ax in axs[-1, :]:
#     ax.set_xlabel(params[count_param])
#     count_param +=1

# # Set y labels only for the first column
# for ax in axs[:, 0]:
#     ax.set_ylabel(outcomes[count_outcomes])
#     count_outcomes += 1

#plt.xticks([0.01, 0.03, 0.1, 0.3], ["0.01", "0.03", "0.1", "0.3"])
plt.tight_layout()
plt.show()

# axs[ycount,xcount].set(xticks=range(0, 0.3), xticklabels=['0.01', '0.03', '0.1', '0.3']);


