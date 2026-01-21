import streamlit as st
from data import *
import altair as alt
from customize import *
from misc.gkzList import *


## PALETTE
palette = get_palette()

st.set_page_config(page_title="Verkehr in der Koralmbahnregion", layout="wide")

st.write('# Verkehr in der Koralmbahnregion')
st.sidebar.title("Einstellungen")


def select_messstelle(values: str) -> str:
    key = [key for key, value in zaehlstellen.items() if value == values]
    if key:
        return key[0]
    else:
        return None

## CONSTANTS
START_JAHR: int = 2012
END_JAHR: int = 2024

## SIDEBAR
with st.sidebar:
    selected_value = st.selectbox('Zählstelle:', zaehlstellen.values(), index=5)

    selected_jahre: int = st.slider("Startjahr",
            min_value=START_JAHR,
            max_value=END_JAHR-1,
            value=(START_JAHR, END_JAHR),
            step=1)
    
    select_start_jahr: int = selected_jahre[0]
    select_end_jahr: int = selected_jahre[1]

    select_trend_line = st.checkbox('Trendlinie', True)

    st.image("gfx/stat_ktn_logo.png", width=190)
    st.text('')
    st.image("gfx/stat_stmk_logo.png", width=150)
    st.text('')
    with st.expander(f''':orange[**Info**]''', expanded=False):
        st.write(f'''
                 Quelle:  
                 ASFINAG - Verkehrszählung.
                 ''')
    with st.expander(f''':orange[**Definition**]''', expanded=False):
        st.write(f'''
                 
                 ''')

st.write(f"### Anzahl der Kfz kleiner 3,5t im Bereich {selected_value} beide Fahrtrichtungen")
df = get_data('verkehrszaehlung.csv')
df = filter_start_end_year(df, select_start_jahr, select_end_jahr)
df = df[df['ZAEHLSTELLE'] == (int)(select_messstelle(selected_value))]
df = df[df['FAHRZEUGKLASSE'] == 'Kfz <= 3,5t hzG']
df['DATUM'] = pd.to_datetime(df['JAHR'].astype(str) + '-' + df['MONAT'].astype(str) + '-01')

chart = create_linechart(verkehr_anpassen(df), select_trend_line)

st.altair_chart(chart, use_container_width=True)


st.write(f"### Anzahl der Kfz größer 3,5t im Bereich {selected_value} beide Fahrtrichtungen")
df = get_data('verkehrszaehlung.csv')
df = filter_start_end_year(df, select_start_jahr, select_end_jahr)
df = df[df['ZAEHLSTELLE'] == (int)(select_messstelle(selected_value))]
df = df[df['FAHRZEUGKLASSE'] == 'Kfz > 3,5t hzG']
df['DATUM'] = pd.to_datetime(df['JAHR'].astype(str) + '-' + df['MONAT'].astype(str) + '-01')

chart = create_linechart(verkehr_anpassen(df), select_trend_line)

st.altair_chart(chart, use_container_width=True)


st.write(f"### Anzahl aller Kfz im Bereich {selected_value} beide Fahrtrichtungen")
df = get_data('verkehrszaehlung.csv')
df = filter_start_end_year(df, select_start_jahr, select_end_jahr)
df = df[df['ZAEHLSTELLE'] == (int)(select_messstelle(selected_value))]
df = df[df['FAHRZEUGKLASSE'] == 'Kfz']
df['DATUM'] = pd.to_datetime(df['JAHR'].astype(str) + '-' + df['MONAT'].astype(str) + '-01')

chart = create_linechart(verkehr_anpassen(df), select_trend_line)

st.altair_chart(chart, use_container_width=True)
