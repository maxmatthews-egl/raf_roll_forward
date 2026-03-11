import pandas as pd

############################ MANUAL UPDATES ############################ 
total_risk_path = r"C:\Users\matthewsm\OneDrive - Enstargroup\ERM Risk Folder\Group\Model Risk Management\CTAL\2026\2026 01 Update\0. Data\_sims\5954 (exported by AP)\One-Year Total Risk Sims.csv"
num_sims = 51

management_margin = 45_000_000
enstar_effect = 127_266_997

inv_asset_scale = 1.0401547114643
net_reserves_scale  = 0.94444485445209
######################################################################## 

return_periods = [2,5,10,20,50,100,200,500]
percentiles = [1/rp for rp in return_periods]

#Order for columns to be displayed
col_order = [ "Total Insurance Risk",
    "Total Market Risk",
    "Total Credit Risk",
    "Total Operational Risk",
    "Total SCR"
]

df = pd.read_csv(total_risk_path)

#Removing non egl_group fields
df = df.loc[(df['Entity'] == 'egl_group')]

#Manipulating table for ease in excel
df = df.pivot(index='Sim', columns='Risk', values='Value')
df = df.reset_index()  # brings back sim column

#Scaling insurance and market risk
mu = df['Total Insurance Risk'].mean()
df['Total Insurance Risk'] = mu + net_reserves_scale * (df['Total Insurance Risk'] - mu)
df['Total Market Risk'] *= inv_asset_scale

#Update Total SCR
df["Total SCR"] = (
      df["Total Credit Risk"]
    + df["Total Insurance Risk"]
    + df["Total Market Risk"]
    + df["Total Operational Risk"])


#DF Can now be exported for plotting in AllRisk

#Finding corridor for sims
tot_sims = len(df)
lower_bound = int(tot_sims*0.05 - num_sims//2 - 1)
upper_bound = int(tot_sims*0.05 + num_sims//2)

corridor = df.sort_values(by = df.columns[-1])
corridor = corridor.reindex(columns=col_order)
corridor = corridor[lower_bound:upper_bound]

#Taking percentiles and ajusting cols
loss_table = df.drop(columns=['Risk','Sim'], errors = 'ignore')
loss_table = loss_table.quantile(percentiles)
loss_table = loss_table.reset_index()

#Convert to Milions for all but first col
loss_table = loss_table.iloc[:,1:]/1_000_000

#Formatting Headers
headers = [f'1 in {rp} Year' for rp in return_periods]

#Insert return periods, reorder and transpose
loss_table.insert(0, 'Return Period', headers)


loss_table = loss_table.reindex(columns=col_order)
loss_table = loss_table.T

#print(loss_table)

#Finding Insurance and RI Credit risk Buffer
ins_and_credit = df['Total Credit Risk'] + df['Total Insurance Risk']
ins_and_credit = ins_and_credit.quantile(0.05) + management_margin - enstar_effect
ins_and_credit = pd.DataFrame({'Insurance and Credit Risk Buffer': [ins_and_credit]})


#Write to excel
loss_table.to_excel('Outputs/total_risk_table.xlsx', index = False)
corridor.to_excel('Outputs/simulation_corridor_data.xlsx', index = False)
ins_and_credit.to_excel('Outputs/insurance_risk_buffer.xlsx', index = False)


##ALTERNATE EXPORT OPTION
#with pd.ExcelWriter(output_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
#    table.to_excel(writer, sheet_name="total_risk_table", index=False)
#    corridor.to_excel(writer, sheet_name="simulation_corridor", index=False)
#    ins_and_credit.to_excel(writer, sheet_name="ins_and_credit", index=False)


