import pandas as pd
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from itertools import cycle
from total_risk_exports import df

tableHalfWindow = 50
numDPs = 1
headerColor = 'royalblue'
rowEvenColor = 'lightblue'
rowOddColor = 'white'
fontColor = 'darkslategray'
headerFontColor = 'white'

totalRiskFile = df / 1_000_000

def create_stacked_bar(
    sims,
    yLabel,
    mapping,
    mappingName,
    mapWithPercentages,
    convertToRisk,
    breakeven,
    numberOfBuckets,
    startPercentile,
    endPercentile,
    color_map=None,
    stack_order=None  # NEW
):
    default_palette = cycle(px.colors.qualitative.G10)
    mappedSims, mappedSimsRisk, spreadVAR = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    numberOfSims = len(sims.index)
    percentiles = []
    svarWindow = [round(numberOfSims * 0.995) - tableHalfWindow, round(numberOfSims * 0.995) + tableHalfWindow]

    if mapWithPercentages:
        for item in list(mapping.index):
            mappedSims[item] = np.zeros(numberOfSims)
            spreadVAR[item] = None
        for column in sims:
            if column in mapping:
                for item in list(mapping.index):
                    mappedSims[item] = mappedSims[item] + sims[column] * mapping[column][item]
            else:
                print("Error: no mapping supplied for: " + column)
                break
    else:
        for column in sims:
            if column in mapping:
                mapTo = mapping[column].iloc[0]
                if mapTo not in mappedSims:
                    mappedSims[mapTo] = sims[column]
                    spreadVAR[mapTo] = None
                else:
                    mappedSims[mapTo] = mappedSims[mapTo] + sims[column]
            else:
                print("Error: no mapping supplied for: " + column)
                break

    mappedNames = spreadVAR.columns.values.tolist()
    mappedSims['Total'] = mappedSims.sum(axis=1)
    mappedSims['Total SCR'] = totalRiskFile['Total SCR']
    mappedSims.sort_values('Total SCR', ascending=False, inplace=True)
    mappedSimsRisk = (mappedSims - mappedSims.mean(axis=0)) * -1
    mappedSimsRisk.sort_values('Total SCR', ascending=True, inplace=True)

    del mappedSims['Total SCR']
    del mappedSimsRisk['Total SCR']

    toPlot = mappedSimsRisk if convertToRisk else mappedSims
    yAxisLabel = "Insurance risk" if convertToRisk else yLabel

    def svar_calc(sims, lowerSim, upperSim):
        section = sims.iloc[lowerSim:upperSim]
        averageOfSection = section.mean(axis=0).to_frame().T
        return averageOfSection

    for i in range(numberOfBuckets):
        lowerPecentile = startPercentile + (endPercentile - startPercentile) * i / numberOfBuckets
        upperPercentile = startPercentile + (endPercentile - startPercentile) * (i + 1) / numberOfBuckets
        lower = math.floor(lowerPecentile * numberOfSims)
        upper = math.floor(upperPercentile * numberOfSims)
        svar = svar_calc(toPlot, lower, upper)
        spreadVAR = pd.concat([spreadVAR, svar], axis=0)
        percentiles.append((lowerPecentile + upperPercentile) / 2)

    fig = make_subplots()

    # --- UPDATED: Use stack_order if provided ---
    plot_order = stack_order if stack_order else mappedNames

    for item in plot_order:
        if item in spreadVAR.columns:
            color = color_map.get(item, next(default_palette)) if color_map else next(default_palette)
            fig.append_trace(go.Bar(
                name=item,
                x=percentiles,
                y=spreadVAR[item],
                marker_color=color
            ), row=1, col=1)
        else:
            print(f"[WARNING] '{item}' not found in spreadVAR columns.")

    # Add total line
    fig.append_trace(go.Scatter(
        x=percentiles,
        y=spreadVAR['Total'],
        name='Total',
        line=dict(width=3, color='black')
    ), row=1, col=1)

    if convertToRisk:
        fig.append_trace(go.Scatter(
            x=[0, 1],
            y=[0, 0],
            line=dict(color='grey', width=2),
            showlegend=False,
            mode='lines'
        ), row=1, col=1)

    fig.update_layout(
        barmode='relative',
        xaxis={'dtick': (endPercentile - startPercentile) / 10},
        font=dict(size=11, color=fontColor)
    )

    axis = np.arange(startPercentile, endPercentile + 10, (endPercentile - startPercentile) / 10)
    axis_percent = np.arange(startPercentile * 100, (endPercentile * 100) + 10, (endPercentile - startPercentile) * 10)
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=axis,
            ticktext=axis_percent
        ),
        width=1400,
        margin=dict(l=0, r=20, b=0, t=0),
        font=dict(size=18, color="rgb(0,30,64)"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.03,
            xanchor="left",
            x=0.01
        )
    )

    # Breakeven Line
    if breakeven:
        if convertToRisk:
            indices = np.argmax(spreadVAR["Total"] < 0)
            ycoords = [spreadVAR['Total'].iloc[0], spreadVAR['Total'].iloc[-1]]
        else:
            indices = np.argmax(spreadVAR["Total"] > mappedSims['Total'].mean())
            ycoords = [0, spreadVAR['Total'].iloc[-1]]
        fig.add_trace(go.Scatter(
            x=[percentiles[indices], percentiles[indices]],
            y=[ycoords[0], ycoords[1]],
            mode='lines',
            line_width=3,
            line_dash="dash",
            line_color='rgb(0,30,64)',
            name='Mean'
        ))
        fig.add_annotation(
            x=percentiles[indices] - 0.01,
            y=spreadVAR['Total'].iloc[indices] + 50,
            text=str(round(percentiles[indices] * 100)) + "%",
            showarrow=True,
            arrowhead=1
        )

    fig.update_xaxes(range=[startPercentile, endPercentile], title_text='Percentile(th)', row=1, col=1)

    return fig
