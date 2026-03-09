import pandas as pd
from generateGraph import create_stacked_bar
from total_risk_exports import df

#### Note this approach avoids using the data cleaning files and simply pushes through an organsied dataframe ####
#### See total_risk_sims_extraction for the filtering process. An update must also be made to totalRiskFile variable in generate graph ####
#### Documentation to be added in README ####

numberOfClasses = 5
unitConversionToBillion = 1_000_000_000

# Load simulation data
sims = df / unitConversionToBillion
del sims['Sim']
del sims['Total SCR']



# Define mapping information
mappingName = "total risk by subrisk"
yLabel = "Subrisk"
excelFilePath = "map.xlsx"
mapping = pd.read_excel(
    excelFilePath,
    sheet_name=mappingName,
    index_col=0,
    nrows=numberOfClasses,
    usecols="A:B",
    header=None
).T

# Define custom RGB colors for subrisks (adjust as needed)
color_map = {
    'Premium Risk': 'rgb(155,160,56)',
    'Insurance Risk': 'rgb(168,20,255)',
    'Credit Risk': 'rgb(114,26,36)',
    'Market Risk': 'rgb(0,0,100)',
    'Operational Risk': 'rgb(0,0,255)'
}

# Create the chart with custom colors
fig = create_stacked_bar(
    sims, yLabel, mapping, mappingName,
    mapWithPercentages=False,
    convertToRisk=False,
    breakeven=False,
    numberOfBuckets=200,
    startPercentile=0,
    endPercentile=1,
    color_map=color_map
)

fig.update_yaxes(title_text="Risk charge ($bn)", range=[-3, 4])
fig.write_image("Outputs/total_risk_chart.png")