from data import *
import altair as alt
from customize import *


# PAGE CONSTANTS
START_JAHR: int = 2004
END_JAHR: int = 2025

## PAGE CONFIG
st.set_page_config(page_title="Wirtschaft in der Koralmbahnregion", layout="wide")

## TITLE
st.title("Wirtschaft in der Koralmbahnregion")

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
                 AMS.
                 ''')
    with st.expander(f''':orange[**Definition**]''', expanded=False):
        st.write(f'''
                **Ein- und auspendelnde Erwerbstätige:** Die Statistik über die ein- und auspendelnden Erwerbstätigen zeigt auf, welche Wege von Erwerbstätigen zurückgelegt werden, um den zu erreichen.

                **Arbeitsstätte:** Ist definiert als jede auf Dauer eingerichtete, durch Name (oder Bezeichnung) und Anschrift gekennzeichnete Einheit, in der mindestens eine Person erwerbstätig ist.

                **Betriebsgrößenstruktur:** Zuordnung der Unternehmen nach der Anzahl ihrer Beschäftigten:  
                 Kleinstunternehmen: 1-9,  
                 Kleinunternehmen: 10-49,  
                 Mittlere Unternehmen: 50-249,  
                 Großunternehmen: ab 250 Beschäftigte.

                **Arbeitslose:** Personen, welche beim AMS als arbeitslos gemeldet sind.

                **Nächtigungen (Tourismus):** Die monatlichen Nächtigungen der Gäste aus dem In- und Ausland werden im Rahmen der Beherbergungsstatistik und auf Basis der Tourismus-Statistik-Verordnung erhoben.

                 ''')

### Ein- und  auspendelnde Erwerbstätige ###
st.write('#### Ein- und  auspendelnde Erwerbstätige')
df = get_data('erwerbstaetige.csv')

df = filter_start_end_year(df, select_start_jahr, select_end_jahr)

df_saldo = df.groupby('JAHR', as_index=False)['ANZAHL'].sum()

group_order = ['Einpendelnde Ktn/Stmk', 'Auspendelnde Ktn/Stmk', 'Einpendelnde Ö', 'Auspendelnde Ö']
df['ANZAHL_FORMATTED'] = df['ANZAHL'].apply(lambda x: add_thousand_dot(str(x)))
df_saldo['ANZAHL_FORMATTED'] = df_saldo['ANZAHL'].apply(lambda x: add_thousand_dot(str(x)))

line_chart = alt.Chart(df_saldo).mark_line(size=4).encode(
    x='JAHR:O',
    y='ANZAHL:Q',
    color=alt.value(palette[6]), 
    tooltip=[alt.Tooltip('JAHR:O', title='Jahr'), alt.Tooltip('ANZAHL_FORMATTED:N', title='Saldo')]
)

stacked_bar_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('JAHR:O', title='Jahr', axis=alt.Axis(labelAngle=45)),  
    y=alt.Y('ANZAHL:Q', title='Anzahl'), 
    color=alt.Color('TYPE:N', 
                    title='Pendelndetyp', 
                    sort=group_order, 
                    legend=alt.Legend(orient='bottom',
                    direction='vertical',
                    columns=3), 
                    scale=alt.Scale(domain=['Einpendelnde Ktn/Stmk', 'Auspendelnde Ktn/Stmk', 'Einpendelnde Ö', 'Auspendelnde Ö', 'Saldo'],
                                    range=[palette[0], palette[0], palette[1], palette[1], palette[6]])),
    tooltip=[alt.Tooltip('JAHR:O', title='Jahr'), 
             alt.Tooltip('TYPE:N', title='pendelndetyp'),
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

combined_chart = alt.layer(stacked_bar_chart, line_chart, white_line, hover_points).configure_axis(
            titleFontWeight='bold'  
        ).configure_legend(
            titleFontWeight='bold'  
        )

if not df.empty:
    st.altair_chart(combined_chart, use_container_width=True)
else:
    st.write(NO_DATA)

### Arbeitsstätten nach Größengruppen ###
st.write('#### Arbeitsstätten nach Größengruppen')

df = get_data('arbeitsstaetten.csv')
df = filter_start_end_year(df, select_start_jahr, select_end_jahr)

df['ANZAHL_FORMATTED'] = df['ANZAHL'].apply(lambda x: add_thousand_dot(str(x)))
group_order = ['Kleinstunternehmen', 'Kleinunternehmen', 'Mittlere Unternehmen', 'Großunternehmen']


if not df.empty:
    log_onoff = st.radio("linear/log", ['lineare Skala', 'logarithmische Skala'], label_visibility='hidden', index=1) 
else:
    log_onoff = 'lineare Skala'

color_encoding = alt.Color('TYPE:N',
                           sort=group_order,
                           title='Größengruppe',
                           legend=alt.Legend(orient='bottom', direction='vertical', columns=5),
                           scale=alt.Scale(range=palette))


if (log_onoff=='logarithmische Skala'):

    line_chart = alt.Chart(df).mark_line(size=4).encode(
        x=alt.X('JAHR:O', title='Jahr', axis=alt.Axis(labelAngle=45)),
        y=alt.Y('sum(ANZAHL)', title='Anzahl (log)').scale(type="log"),
        color=color_encoding,
        tooltip=[alt.Tooltip('JAHR:O', title='Jahr'), 
                alt.Tooltip('TYPE:N', title='Arbeitsstätte'),
                alt.Tooltip('ANZAHL_FORMATTED:N', title='Anzahl')]
    )

    hover_points = alt.Chart(df).mark_circle(size=6000, opacity=0).encode(
        x=alt.X('JAHR:O', title='Jahr'),
        y=alt.Y('sum(ANZAHL)', title='Anzahl (log)').scale(type="log"),
        color=color_encoding,
        tooltip=[alt.Tooltip('JAHR:O', title='Jahr'), 
                alt.Tooltip('TYPE:N', title='Arbeitsstätte'),
                alt.Tooltip('ANZAHL_FORMATTED:N', title='Anzahl')]
        )
    
    combined_chart = (line_chart + hover_points).properties(
                width=800,
                height=600
            ).configure_axis(
                titleFontWeight='bold'  
            ).configure_legend(
                titleFontWeight='bold'  
            )

else:
    combined_chart = alt.Chart(df).mark_line(size=4).encode(
        x=alt.X('JAHR:O', title='Jahr', axis=alt.Axis(labelAngle=45)),
        y=alt.Y('sum(ANZAHL)', title='Anzahl'),
        color=color_encoding,
        tooltip=[alt.Tooltip('JAHR:O', title='Jahr'), 
                alt.Tooltip('TYPE:N', title='Arbeitsstätte'),
                alt.Tooltip('ANZAHL_FORMATTED:N', title='Anzahl')]
    ).properties(
                width=800,
                height=600
    ).configure_axis(
        titleFontWeight='bold'  
    ).configure_legend(
        titleFontWeight='bold'  
    )

if not df.empty:    
    st.altair_chart(combined_chart, use_container_width=True)
else:
    st.write(NO_DATA)

### Arbeitslose nach Geschlecht ###
st.write('#### Arbeitslose nach Geschlecht')

df = get_data('arbeitslose.csv')
df['JAHR'] = df['DATUM'].str[:4]
df['JAHR'] = df['JAHR'].astype(int)
df = df[df['JAHR'] < UNIVERSAL_END_YEAR] 
df = filter_start_end_year(df, select_start_jahr, select_end_jahr)

df['ANZAHL_FORMATTED'] = df['ANZAHL'].apply(lambda x: add_thousand_dot(str(x)))

stacked_bar_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('DATUM:O', title='Jahr', axis=alt.Axis(labelAngle=45)),  
    y=alt.Y('ANZAHL:Q', title='Anzahl'), 
    color=alt.Color('GESCHLECHT:N', 
                    title='Geschlecht', 
                    legend=alt.Legend(orient='bottom',
                    direction='vertical',
                    columns=2), 
                    scale=alt.Scale(range=palette)),
    tooltip=[alt.Tooltip('DATUM:O', title='Monat'), 
             alt.Tooltip('GESCHLECHT:N', title='Geschlecht'),
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


### Nächtigungen nach Jahr/Monat ###
st.write('#### Nächtigungen nach Jahr/Monat')

monats_name_mapping = {'1': 'Jänner', '2': 'Feber', '3': 'März', '4':' April', '5': 'Mai', '6': 'Juni', '7': 'Juli', '8': 'August', '9': 'September', '10': 'Oktober', '11': 'November', '12': 'Dezember'}

df = get_data('tourismus.csv')

df = df[df['JAHR'] >= select_start_jahr]
df = df[df['JAHR'] <= select_end_jahr]
df = df[df['JAHR'] < UNIVERSAL_END_YEAR]

if not df.empty:
    year_month = st.radio("Jahr/Monat", ['Jahr', 'Monat'], label_visibility='hidden', index=1)
else:
    year_month = 'Monat'
if(year_month=='Monat'):   

    df = df.groupby(['JAHR', 'MONAT']).agg({'UEBERNACHTUNGEN': 'sum'}).reset_index()
else:
    df = df.groupby(['JAHR']).agg({'UEBERNACHTUNGEN': 'sum'}).reset_index()
    df['Kat'] = 1
    df_kat2 = df.copy()
    df_kat2['Kat'] = 2
    df_kat2['UEBERNACHTUNGEN'] = 0

    df = pd.concat([df, df_kat2], ignore_index=True)

df['ANZAHL_FORMATTED'] = df['UEBERNACHTUNGEN'].apply(lambda x: add_thousand_dot(str(x)))

if(year_month=='Monat'):

    df['MONAT_NAME'] = df['MONAT'].apply(lambda x: monats_name_mapping.get(str(x)))
    stacked_bar_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('JAHR:O', 
                    title='Jahr',
                    axis=alt.Axis(labelAngle=45)),
            y=alt.Y('UEBERNACHTUNGEN:Q', 
                    title='Anzahl'
                    ),
            color=alt.Color(
                'MONAT:N', 
                title='Monat', 
                scale=alt.Scale(range=tourismus_palette),
                legend=alt.Legend(orient='bottom',
                        direction='vertical',
                        columns=6, 
                        labelExpr='datum.value == "1" ? "Jänner" : '
                    'datum.value == "2" ? "Feber" : '
                    'datum.value == "3" ? "März" : '
                    'datum.value == "4" ? "April" : '
                    'datum.value == "5" ? "Mai" : '
                    'datum.value == "6" ? "Juni" : '
                    'datum.value == "7" ? "Juli" : '
                    'datum.value == "8" ? "August" : '
                    'datum.value == "9" ? "September" : '
                    'datum.value == "10" ? "Oktober" : '
                    'datum.value == "11" ? "November" : '
                    'datum.value == "12" ? "Dezember" : datum.value'
        ), 
            ),
            order=alt.Order('JAHR:N', sort='ascending'),
            tooltip=[
                alt.Tooltip('JAHR:O', 
                            title='Jahr'), 
                alt.Tooltip('MONAT_NAME:N', 
                            title='Monat'), 
                alt.Tooltip('ANZAHL_FORMATTED:N', 
                            title='Anzahl'),
            ],
        ).properties(
            width=800,
            height=600
        ).configure_axis(
        titleFontWeight='bold'  
        ).configure_legend(
            titleFontWeight='bold'  
        )
else:     
    stacked_bar_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('JAHR:O', 
                    title='Jahr',
                    axis=alt.Axis(labelAngle=45)),
            y=alt.Y('UEBERNACHTUNGEN:Q', 
                    title='Anzahl'
                    ),
                    color=alt.Color(
                    'Kat:N',
                     scale=alt.Scale(domain=[1], range=[palette[0]]),legend=alt.Legend(orient='bottom', 

                                    title='_',
                                    columns=1, 
                                    titleOpacity=0, 
                                    labelOpacity=0, 
                                    symbolOpacity=0
                                    )), 
                order=alt.Order('JAHR:N', sort='ascending'),
                tooltip=[
                    alt.Tooltip('JAHR:O', 
                                title='Jahr'), 
                    alt.Tooltip('ANZAHL_FORMATTED:N', 
                                title='Anzahl'),
                ],
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