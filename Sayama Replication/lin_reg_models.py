import pandas as pd 
import statsmodels.api as sm


data = pd.read_csv("statistics.csv") # turns csv file of data to a dataframe

# gets the parameter values 
col_cs = data["c"]
col_hs = data["h"]
col_as = data["a"]
col_theta_hs = data["theta_h"]
col_theta_as = data["theta_a"]

# calculates the interactions between parameters
cs_hs = col_cs * col_hs
cs_as = col_cs * col_as 
cs_theta_hs = col_cs * col_theta_hs  
cs_theta_as = col_cs * col_theta_as
hs_as = col_hs * col_as 
hs_theta_hs = col_hs * col_theta_hs 
hs_theta_as = col_hs * col_theta_as 
as_theta_hs = col_as * col_theta_hs 
as_theta_as = col_as * col_theta_as 
thetas = col_theta_hs * col_theta_as 

# creates matrix X which has each column being a parameter value or interaction
X = pd.concat([col_cs, col_hs, col_as, col_theta_hs, col_theta_as
               , cs_hs, cs_as, cs_theta_hs, cs_theta_as, 
               hs_as, hs_theta_hs, hs_theta_as, as_theta_hs, as_theta_as, thetas], axis=1)
X.columns = ["c" , "h" , "a", "theta_h" , "theta_a" , "ch" , "ca" , "cth", "cta", "ha", "hth", "hta",
             "ath", "ata", "thta"]
X = sm.add_constant(X) # adds a columns of 1s to account for the intercept

regression_coefs = {"average edge weight" : [], "number of communites" : [] ,
                    "modularity" : [], "range of avg comm. states" : [], 
                    "std. of avg comm.states" : []} # stores the coefficents for each outcome

for outcome in regression_coefs:
    y = data[outcome] # value we want to predict 
    print(y)
    print(X)
    model = sm.OLS(y, X) # OLS linear regression model
    results = model.fit()
    # print(results.summary())
    #print(results.params)
    regression_coefs[outcome].append(results.params) # stores the coefficents

print(regression_coefs)













