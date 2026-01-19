import streamlit as st
import pandas as pd
from misc.gkzList import gkzList

HOVER_SIZE = 700
HOVER_OPACITY = 0
UNIVERSAL_END_YEAR = 2025
NO_DATA = "Keine Daten für den gewünschten Zeitraum."

@st.cache_data  
def get_data(fileName: str) -> pd.DataFrame:
    try:
        df: pd.DataFrame = pd.read_csv(f'data/{fileName}', sep=';', decimal=',')
    except:
        df = pd.DataFrame()
    return df

def filter_start_end_year(df: pd.DataFrame, start_jahr: int, end_jahr: int) -> pd.DataFrame:
    df = df[df['JAHR'] >= start_jahr]
    df = df[df['JAHR'] <= end_jahr]
    return df
 
def filter_gkz(df: pd.DataFrame, gkz: str) -> pd.DataFrame:
    df = df[df[gkz].astype(str).isin(gkzList['gkz'])]
    return df

if __name__ == '__main__':
    pass

    