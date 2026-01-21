from data import *
import altair as alt
from customize import *

# PAGE CONSTANTS
START_JAHR: int = 2002
END_JAHR: int = 2025

## PAGE CONFIG
st.set_page_config(page_title="Bevölkerung in der Koralmbahnregion", layout="wide")

## TITLE
st.title("Bevölkerung in der Koralmbahnregion")

## PALETTE
palette = get_palette()

## SIDEBAR
with st.sidebar:
    selected_jahre: int = st.slider("Startjahr",
            min_value=START_JAHR,
            max_value=END_JAHR-1,
            value=(START_JAHR, END_JAHR),
            step=1)
    
    select_start_jahr: int = selected_jahre[0]
    select_end_jahr: int = selected_jahre[1]

    st.image("gfx/stat_ktn_logo.png", width=190)
    st.text('')
    st.image("gfx/stat_stmk_logo.png", width=150)
    st.text('')
    with st.expander(f''':orange[**Info**]''', expanded=False):
        st.write(f'''
                 Quellen:  
                 Landesstellen für Statistik,  
                 Grundstückspreise: Statistik Austria.
                 ''')
    with st.expander(f''':orange[**Definition**]''', expanded=False):
        st.write(f''' 
                **Bevölkerung:** Umfasst alle Personen, die zum Stichtag 01.01. des jeweiligen Jahres mit Hauptwohnsitz in der Koralmbahnregion gezählt wurden.
                
                **Wanderung:** Beschreibt die räumliche Mobilität von Personen zur Errichtung eines dauerhaften Hauptwohnsitzes.

                **Durchschnittliche Grundstückspreise:** Bilden das durchschnittliche Preisniveau von Grundstücken in der Koralmbahnregion ab. Zur Berechnung der Werte des Zieljahres werden auch die Transaktionen der vier Vorjahre berücksichtigt (Regressionsmodell).

                **Wohnung:** Bezeichnet baulich getrennte Einheiten mit eigenem Zugang von der Straße oder einem Stiegenhaus in dauerhaften Gebäuden, die für Wohnzwecke geeignet sind.
                
                **Bauperiode:** Bezeichnet den Zeitraum, in dem das Errichtungsdatum des Gebäudes liegt.

                 ''')

### Bevölkerung nach Altersgruppen ###
st.write("#### Bevölkerung nach Altersgruppen")

df = get_data('bevoelkerung.csv')

df = filter_start_end_year(df, select_start_jahr, select_end_jahr)

anteil_anzahl = st.radio("Anteil/Anzahl", ['Anteil', 'Anzahl'], label_visibility='hidden', index=1)

group_order = ['bis 20 Jahre', 'zw. 20 und 64 Jahren', 'über 65 Jahre']

if (anteil_anzahl == 'Anteil'):
    df['ANTEIL'] = df['ANZAHL'] / df.groupby('JAHR')['ANZAHL'].transform('sum') * 100
    df['ANTEIL_FORMATTED'] = df['ANTEIL'].apply(lambda x: handle_comma(str(round(x,1))))
    stacked_bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('JAHR:O', title='Jahr', axis=alt.Axis(labelAngle=45)),  
        y=alt.Y('ANTEIL:Q', title='Anteil in %'),
        color=alt.Color('GRUPPE:N', 
                        title='Altersgruppe', 
                        sort=group_order, 
                        scale=alt.Scale(domain=group_order, range=palette),
                        legend=alt.Legend(orient='bottom',
                                        direction='vertical',
                                        columns=3)),
        order=alt.Order('GRUPPE:N', 
                        sort='ascending'),
        tooltip=[alt.Tooltip('JAHR:O', title='Jahr'), 
                alt.Tooltip('GRUPPE:N', title='Altersgruppe'),
                alt.Tooltip('ANTEIL_FORMATTED:N', title='Anteil in %')],
        ).properties(
                width=800,
                height=600
                ).configure_axis(
                    titleFontWeight='bold'
                ).configure_legend(
                    titleFontWeight='bold'  
                ).properties(
                usermeta={
                    "embedOptions": custom_locale
                }
            )
else:
    df['ANZAHL_FORMATTED'] = df['ANZAHL'].apply(lambda x: add_thousand_dot(str(x)))
    stacked_bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('JAHR:O', title='Jahr', axis=alt.Axis(labelAngle=45)),  
        y=alt.Y('ANZAHL:Q', title='Anzahl'),
        color=alt.Color('GRUPPE:N', 
                        title='Altersgruppe', 
                        sort=group_order, 
                        scale=alt.Scale(domain=group_order, range=palette),
                        legend=alt.Legend(orient='bottom',
                                        direction='vertical',
                                        columns=3)),
        order=alt.Order('GRUPPE:N', 
                        sort='ascending'),
        tooltip=[alt.Tooltip('JAHR:O', title='Jahr'), 
                alt.Tooltip('GRUPPE:N', title='Altersgruppe'),
                alt.Tooltip('ANZAHL_FORMATTED:N', title='Anzahl')],
        ).properties(
                width=800,
                height=600
                ).configure_axis(
                    titleFontWeight='bold'
                ).configure_legend(
                    titleFontWeight='bold'  
                ).properties(
                usermeta={
                    "embedOptions": custom_locale
                }
            )

if not df.empty:
    st.altair_chart(stacked_bar_chart, use_container_width=True)
else:
    st.write(NO_DATA)


### Wanderungen nach Wanderungstyp ###
st.write("#### Wanderungen nach Wanderungstyp")

df = get_data('wanderungen.csv')
df = filter_start_end_year(df, select_start_jahr, select_end_jahr)

findmax = df.groupby('JAHR').agg({'ANZAHL': 'sum'}).reset_index()
max_value = max(abs(findmax['ANZAHL'].min()), abs(findmax['ANZAHL'].max()))

df_saldo = df.groupby('JAHR', as_index=False)['ANZAHL'].sum()

df['ANZAHL_FORMATTED'] = df['ANZAHL'].apply(lambda x: add_thousand_dot(str(x)))
df_saldo['ANZAHL_FORMATTED'] = df_saldo['ANZAHL'].apply(lambda x: add_thousand_dot(str(x)))

only_line_chart = alt.Chart(df_saldo).mark_line(size=5).encode(
    x='JAHR:O',
    y='ANZAHL:Q',
    color=alt.value(palette[6]), 
    tooltip=[alt.Tooltip('JAHR:O', title='Jahr'), 
             alt.Tooltip('ANZAHL_FORMATTED:N', title='Saldo')]
)

group_order = ['Zuwanderung KTN/STK', 'Abwanderung KTN/STK', 'Zuwanderung Ö', 'Abwanderung Ö', 'Zuwanderung Ausland', 'Abwanderung Ausland']

stacked_bar_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('JAHR:O', title='Jahr', axis=alt.Axis(labelAngle=45)),  
    y=alt.Y('ANZAHL:Q', title='Anzahl', 
            ), 
    color=alt.Color('TYPE:N', 
                     title='Wanderungstyp', 
                    sort=group_order, 
                    legend=alt.Legend(orient='bottom',
                    direction='vertical',
                    columns=4), 
                    scale=alt.Scale(domain=['Zuwanderung KTN/STK', 'Abwanderung KTN/STK', 'Zuwanderung Ö', 'Abwanderung Ö', 'Zuwanderung Ausland', 'Abwanderung Ausland', 'Saldo'], 
                                    range=[palette[0], palette[0], palette[1], palette[1], palette[2], palette[2], palette[6]])
                   ),
    tooltip=[alt.Tooltip('JAHR:O', title='Jahr'), 
             alt.Tooltip('TYPE:N', title='Wanderungstyp'),
             alt.Tooltip('ANZAHL_FORMATTED:N', title='Anzahl')],
    ).properties(
    width=800,
    height=600
)

white_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='white').encode(
    y='y'
)

hover_points = alt.Chart(df_saldo).mark_circle(size=HOVER_SIZE, opacity=HOVER_OPACITY).encode(
    x='JAHR:O',
    y='ANZAHL:Q',
    tooltip=[alt.Tooltip('JAHR:O', title='Jahr'), alt.Tooltip('ANZAHL_FORMATTED:N', title='Saldo')] 
)

combined_chart = alt.layer(stacked_bar_chart, only_line_chart, white_line, hover_points).configure_axis(
            titleFontWeight='bold'  
        ).configure_legend(
            titleFontWeight='bold'  
        )


if not df.empty:
    st.altair_chart(combined_chart, use_container_width=True)
else:
    st.write(NO_DATA)


### Durchschnittliche Grundstückspreise in Euro ###
st.write("#### Durchschnittliche Grundstückspreise in Euro")
df = get_data('grundstueckspreise.csv')

df = filter_start_end_year(df, select_start_jahr, select_end_jahr)

df['Preis_FORMATTED'] = df['Preis'].apply(lambda x: handle_comma(x))
group_order=['< 5.000 EW', '5.000 - 10.000 EW', '10.000 - 50.000 EW', '> 50.000 EW']

hover_points = alt.Chart(df).mark_circle(size=1000, opacity=HOVER_OPACITY).encode(
    x='JAHR:O',
    y='Preis:Q',
    tooltip=[alt.Tooltip('JAHR:O', title='Jahr'), alt.Tooltip('Preis_FORMATTED:N', title='Preis pro m²')] 
)

line_chart = alt.Chart(df).mark_line(size=5).encode(
    x=alt.X('JAHR:O', title='Jahr', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('Preis:Q', title='Preis pro m²'),
    color=alt.Color('GEMTYPE:N', 
                    title='Gemeinden mit ...',
                    sort=group_order,
                    legend=alt.Legend(orient='bottom',
                    direction='vertical',
                    columns=4),
                    scale=alt.Scale(range=[palette[0], palette[1], palette[2], palette[3]])),  
    )

chart = (line_chart + hover_points).properties(
    width=800,
    height=600
).configure_axis(
    titleFontWeight='bold'  
).configure_legend(
    titleFontWeight='bold'  
)

if not df.empty:
    st.altair_chart(chart, use_container_width=True)
else:
    st.write(NO_DATA)

### Wohnungen nach Bauperiode ###
st.write("#### Wohnungen nach Bauperiode")

df = get_data('wohnungen.csv')

df = filter_start_end_year(df, select_start_jahr, select_end_jahr)

df['ANZAHL_FORMATTED'] = df['ANZAHL'].apply(lambda x: add_thousand_dot(str(x)))

group_order = ['bis 1960']
stacked_bar_chart = alt.Chart(df).mark_bar().encode(
x=alt.X('JAHR:O', title='Jahr', axis=alt.Axis(labelAngle=0)),  
y=alt.Y('ANZAHL:Q', title='Anzahl'),
color=alt.Color('BAUPERIODE_A:N', 
                title='Bauperiode', 
                sort=group_order, 
                legend=alt.Legend(orient='bottom',
                                direction='vertical',
                                columns=8), 
                scale=alt.Scale(range=palette)),
order=alt.Order('ANZAHL:Q', 
                sort='descending'),
tooltip=[alt.Tooltip('JAHR:O', title='Jahr'), 
         alt.Tooltip('BAUPERIODE_A:N', title='Bauperiode'),
         alt.Tooltip('ANZAHL_FORMATTED:N', title='Anzahl')],
).properties(
width=800,
height=600
).configure_axis(
    titleFontWeight='bold'  
).configure_legend(
    titleFontWeight='bold'  
)
if not df.empty:
    st.altair_chart(stacked_bar_chart, use_container_width=True)
else:
    st.write(NO_DATA)
