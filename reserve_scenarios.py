import pandas as pd 

############################ MANUAL UPDATES ############################ 
reserve_sim_path = r"C:\\Users\\matthewsm\\OneDrive - Enstargroup\\ERM Risk Folder\\Group\\Model Risk Management\\CTAL\\2026\\2026 01 Update\\0. Data\\_sims\\5954 (exported by AP)\\One-Year Reserve Risk by Class.csv"
num_sims = 51
net_reserves_scale  = 0.94444485445209
######################################################################## 

df = pd.read_csv(reserve_sim_path)
#Finding corridor for sims
tot_sims = len(df)
lower_bound = int(tot_sims*0.05 - num_sims//2 - 1)
upper_bound = int(tot_sims*0.05 + num_sims//2)


#Dropping empty and invalid classes
invalid_classes = ['micl_cbre_qs_assumed', 'lloyds_assumed','sise_cbre_qs_assumed','rti_cbre_qs_assumed']
df = df.dropna(how = 'all', axis = 1) #Drop all N/A cols

#Combining QBE2 into one class
df['qbe2'] = df['qbe_atom23_lloyds'] + df['qbe_atom23_other']
df.insert(1, 'qbe2', df.pop('qbe2'))
df = df.drop(columns=['qbe_atom23_lloyds', 'qbe_atom23_other'])
df = df.drop(columns= invalid_classes)
df['total'] = df.iloc[:,1:].sum(axis = 1) # Creating total col excl. sim number

df.iloc[:,1:] *= net_reserves_scale

df = df.sort_values(by = df.columns[-1])

res_corridor = df[lower_bound:upper_bound]

#print(res_corridor)
res_corridor.to_excel('reserve_scenarios.xlsx', index = False)
