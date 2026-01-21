import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

tourismus_palette = ['#7586ff', 
                 '#98a9ff', 
                 '#c8d9ff',  
                 '#afe1f4', 
                 '#ffc556', 
                 '#ffbf00', 
                 '#f6977a',
                 '#fa8072',
                 '#f9cb9c', 
                 '#feeece',
                 '#003783', 
                 '#00076d']

def LinearRegression(df: pd.DataFrame) -> pd.DataFrame:

    df['DATUM'] = pd.to_datetime(df['DATUM'])
    df['DAYS_NUMERIC'] = (df['DATUM'] - df['DATUM'].min()).dt.days

    x_mean = np.mean(df['DAYS_NUMERIC'])
    df['ANZAHL'] = df['ANZAHL'].astype(float)
    y_mean = np.mean(df['ANZAHL'])

    numerator = np.sum((df['DAYS_NUMERIC'] - x_mean) * (df['ANZAHL'] - y_mean))
    denominator = np.sum((df['DAYS_NUMERIC'] - x_mean) ** 2)
    m = numerator / denominator
    b = y_mean - m * x_mean

    df['REGRESSION'] = m * df['DAYS_NUMERIC'] + b
    return df

def handle_comma(input: float) -> str:
    input = str(input).replace('.', ',')
    return input


def add_thousand_dot(txt: str) -> str:
    if(txt[0] == '-'):
        if(len(txt) > 7):
            txt = txt[::-1]
            txt = txt[:3] + '.' + txt[3:6] + '.' + txt[6:]
            txt = txt[::-1]
        elif(len(txt) > 4):
            txt = txt[::-1]
            txt = txt[:3] + '.' + txt[3:]
            txt = txt[::-1]
    else:
        if(len(txt) > 6):
            txt = txt[::-1]
            txt = txt[:3] + '.' + txt[3:6] + '.' + txt[6:]
            txt = txt[::-1]
        elif(len(txt) > 3):
            txt = txt[::-1]
            txt = txt[:3] + '.' + txt[3:]
            txt = txt[::-1]
    return txt

def custom_css_sytles():
    st.markdown("""
        <style>
            .bokeh-plot-container {
                width: 100% !important;
                height: 100% !important;
            }
        </style>
    """, unsafe_allow_html=True)

def get_palette():
    cud_colors = ['#003B5C', '#FFB81C', '#55B0B9', '#F56D8D', '#9E2A2F', '#5B8C5A', '#CC79A7']
    return cud_colors

def create_linechart(df: pd.DataFrame, reg: int) -> pd.DataFrame:
    palette = get_palette()
    y_min = min(df['ANZAHL'].astype(float).min(), df['REGRESSION'].astype(float).min())
    y_max = max(df['ANZAHL'].astype(float).max(), df['REGRESSION'].astype(float).max())
    df['ANZAHL_FORMATTED'] = df['ANZAHL'].apply(lambda x: add_thousand_dot(str(int(round(x, 0)))))

    chart = alt.Chart(df).mark_line(color=palette[1], size=4).encode(
        x=alt.X('DATUM:T', title='Datum', axis=alt.Axis(format='%Y-%m', labelAngle=45)),
        y=alt.Y('ANZAHL:Q', title='Anzahl', scale=alt.Scale(domain=(y_min, y_max))),
        tooltip=[alt.Tooltip('DATUM:T', title='Datum'), 
             #alt.Tooltip('TYPE:N', title='Arbeitsstätte'),
             alt.Tooltip('ANZAHL_FORMATTED:N', title='Anzahl')]

    )

    hover_points = alt.Chart(df).mark_circle(size=250, opacity=0).encode(
    x=alt.X('DATUM:T', title='Datum'),
    y=alt.Y('ANZAHL:Q', title='Anzahl'),
    tooltip=[alt.Tooltip('DATUM:T', title='Jahr'), 
             alt.Tooltip('ANZAHL_FORMATTED:N', title='Anzahl')]
    )

    df['REG_FORMATTED'] = df['REGRESSION'].apply(lambda x: add_thousand_dot(str(int(round(x, 0)))))
    regression_line = alt.Chart(df).mark_line(color=palette[6], size=2).encode(
            x=alt.X('DATUM:T'),
            y=alt.Y('REGRESSION:Q', title="Trend"),
            tooltip=alt.value(None)
            #[alt.Tooltip('DATUM:T', title='Datum'),
            #         alt.Tooltip('REG_FORMATTED:O', title='Trend')]
        )

    if(reg == False):
        combined_chart = (chart + hover_points).configure_axis(
            titleFontWeight='bold'  
        ).configure_legend(
            titleFontWeight='bold'  
        )
    else:
        combined_chart = (chart + hover_points + regression_line).configure_axis(
            titleFontWeight='bold'  
        ).configure_legend(
            titleFontWeight='bold'  
        )

    return combined_chart
    
def verkehr_anpassen(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(['JAHR', 'MONAT'])
    df['DAYS'] = (df['DATUM'] - df['DATUM'].min()).dt.days
    df = LinearRegression(df)
    df.drop(columns=['JAHR', 'MONAT', 'DAYS'], inplace=True, axis=1)
    return df

## custom locale

custom_locale = {
                "formatLocale": {
                                "decimal": ",",
                                "thousands": ".",
                                "grouping": [3],
                                "currency": ["", "\u00a0€"]
                                },

                "timeFormatLocale": {
                                "dateTime": "%A, der %e. %B %Y, %X",
                                "date": "%d.%m.%Y",
                                "time": "%H:%M:%S",
                                "periods": ["AM", "PM"],
                                "days": ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"],
                                "shortDays": ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],
                                "months": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
                                "shortMonths": ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
                                    }
                }
