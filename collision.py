import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import plotly.express as px

data_url = ('/Users/strawberry/Documents/rdatasets/collision.csv')
midpoint=[40.71427, -73.9212]

@st.cache(persist=True)
def load_data():
    df = pd.read_csv(data_url, parse_dates=[['CRASH DATE', 'CRASH TIME']])
    df.dropna(subset=['LONGITUDE', 'LATITUDE'], inplace = True)
    lowercase = lambda x: str(x).lower()
    df.rename(lowercase, axis=1, inplace=True)
    df.rename(columns={'crash date_crash time': 'date/time'}, inplace=True)
    return df

def show_map(data):
    st.write(pdk.Deck(
        initial_view_state={
            'latitude': midpoint[0],
            'longitude': midpoint[1],
            'zoom': 9.5,
            'pitch': 50,
        },
        layers=[
        pdk.Layer(
        'HexagonLayer',
        data=data,
        get_position=['longitude', 'latitude'],
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=5,
        elevation_range=[0, 1000],
        ),
        ],

    ))
    return

df = load_data()

st.markdown('# Crash Data Analysis (New York)')

st.markdown('### Majority of injuries')
injuries = st.slider("Number of people injured in vehicle crash" , 0, int(df['number of persons injured'].max()))
show_map(df[df['number of persons injured'] >= injuries][['latitude','longitude']].dropna(how='any'))

st.markdown('### Injuries during a given hour')
hour = st.slider('Hour', 0, 23)
df = df[df['date/time'].dt.hour == hour]

st.markdown('### Vehicle collision between %i:00 and %i:00' % (hour, (hour + 1 ) % 24))
show_map(df[['date/time', 'latitude', 'longitude']])

st.markdown('### Breakdown by minute between %i:00 and %i:00' % (hour, (hour + 1) % 24))
filtered = df[
    (df['date/time'].dt.hour >= hour) & (df['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.markdown('### Top 5 dangerous streets based on affected type')
affected = st.selectbox('Affected types', ['Pedestrians', 'Cyclists', 'Motorists'])

if affected == 'Pedestrians':
    pedistrians = df[df['number of pedestrians injured'] >= 1][['off street name', 'number of pedestrians injured']].sort_values(by=['number of pedestrians injured'], ascending=False).dropna(how='any')[:5]
    st.write(pedistrians)

elif affected == 'Cyclists':
    cyclists = df[df['number of cyclist injured'] >= 1][['off street name', 'number of cyclist injured']].sort_values(by=['number of cyclist injured'], ascending=False).dropna(how='any')[:5]
    st.write(cyclists)

else:
    motorists = df[df['number of motorist injured'] >= 1][['off street name', 'number of motorist injured']].sort_values(by=['number of motorist injured'], ascending=False).dropna(how='any')[:5]
    st.write(motorists)






if st.checkbox("Show Raw Data", False):
    st.write(df)
