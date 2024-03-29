from csv import writer

field_names = ['run' , 'c' , 'h', 'a', 'theta_h', 'theta_a' , 'average edge weight' , 
                   'number of communites', 'modularity' , 'range of avg comm. states' , 'std. of avg comm.states'] # fields of the csv file


with open('statistics.csv', 'w') as stats:
    writer_object = writer(stats)
    writer_object.writerow(field_names)
stats.close()