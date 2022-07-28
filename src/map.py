import os
import datetime
import pandas as pd

from render import get_frame, save_gif
from directions import get_json_geometry, get_directions

# Constants
start_datetime = datetime.datetime(2019,7,22,7,59,50)
end_datetime = datetime.datetime(2019,7,22,9,30,0)


# Reading Bixi data into Pandas dataframes
df = pd.read_csv('data/OD_2019-07.csv')
st = pd.read_csv('data/Stations_2019.csv')

# Converting datetimes
df['start_date'] = pd.to_datetime(df['start_date'])
df['end_date'] = pd.to_datetime(df['end_date'])
df['hour'] = df['start_date'].map(lambda x : x.hour)
df['dow'] = df['start_date'].map(lambda x : x.weekday())

# Joining stations metadata to trip data
data = df.merge(st, left_on = 'start_station_code', right_on = 'Code')
data.rename(columns=dict(zip(st.columns.values,["start_station_" + x.lower() for x in st.columns.values])),inplace = True)
data = data.merge(st, left_on = 'end_station_code', right_on = 'Code')
data.rename(columns=dict(zip(st.columns.values,["end_station_" + x.lower() for x in st.columns.values])),inplace = True)
data = data.loc[:,~data.columns.duplicated()]

# Group data by all start/end station combinations and add the trip count
comb = data.groupby([
    'start_station_code',
    'start_station_latitude', 
    'start_station_longitude', 
    'end_station_code',
    'end_station_latitude', 
    'end_station_longitude'
]).size().to_frame('count').reset_index().sort_values('count', ascending = False)

# Remove trips where same start/end status (likely not real trips or edge cases)
routes = comb[(comb['start_station_code'] != comb['end_station_code'])].reset_index(drop=True)


# Pull all the directions from API and store locally
for i, row in routes.iloc[0:30000].iterrows():
    start_coord = (row['start_station_latitude'], row['start_station_longitude'])
    end_coord = (row['end_station_latitude'],row['end_station_longitude'])
    if not os.path.exists(f'directions/%s_%s.json' % (str(int(row['start_station_code'])),str(int(row['end_station_code'])))):
        geom = get_directions(
            start_coord,
            end_coord,
            str(int(row['start_station_code'])),
            str(int(row['end_station_code']))
        )


# Calculate how many frames needed
delta = datetime.timedelta(seconds = 10)
cnt = (end_datetime-start_datetime)/delta

img = []

# Iterate over each timeframe
while start_datetime < end_datetime:
    current_datetime = start_datetime + delta
    curr = cnt - (end_datetime-current_datetime)/delta
    print(f"Processing frame {str(int(curr))} of {str(int(cnt))} ({str(int(curr/cnt*100))}%)")
    subset = data[(data.start_date <= start_datetime) & (data.end_date > current_datetime) & (data.start_station_code != data.end_station_code)]
    subset['geometry'] = subset.apply(lambda row: get_json_geometry(row), axis=1)
    center = [data.start_station_latitude.mean(),data.start_station_longitude.mean()]
    im = get_frame(subset, center, current_datetime)
    img.append(im)
    start_datetime = current_datetime

save_gif(img, 'bixi.gif')
    
