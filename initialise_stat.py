from csv import writer

field_names = ['run' , 'c' , 'h', 'a', 'theta_h', 'theta_a' , 'avg_edw' , 
                   'num_com', 'mod' , 'avg_com' , 'sd_com'] # fields of the csv file


with open('statistics.csv', 'w') as stats:
    writer_object = writer(stats)
    writer_object.writerow(field_names)
stats.close()