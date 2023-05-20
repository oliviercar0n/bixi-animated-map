import datetime
import pandas as pd

from render import get_frame, save_gif
from directions import get_json_geometry, get_directions


pd.options.mode.chained_assignment = None


# Constants
START_DATETIME = datetime.datetime(2022, 8, 22, 7, 0, 0)
END_DATETIME = datetime.datetime(2022, 8, 22, 10, 0, 0)
TRIP_FILE_PATH = "../data/20220108_donnees_ouvertes.csv"
STATION_FILE_PATH = "../data/20220108_stations.csv"

# Reading Bixi data into Pandas dataframes
print("Reading data files...")
df = pd.read_csv(TRIP_FILE_PATH)
st = pd.read_csv(STATION_FILE_PATH)

df.columns = [
    "start_date",
    "start_station_code",
    "end_date",
    "end_station_code",
    "duration_sec",
    "is_member",
]

st.columns = ["Code", "name", "latitude", "longitude"]

# Converting datetimes
print("Formatting dataframe dates...")
df["start_date"] = pd.to_datetime(df["start_date"])
df["end_date"] = pd.to_datetime(df["end_date"])
df["hour"] = df["start_date"].map(lambda x: x.hour)
df["dow"] = df["start_date"].map(lambda x: x.weekday())


# Joining stations metadata to trip data
print("Joining stations metadata to trip data...")
data = df.merge(st, left_on="start_station_code", right_on="Code")
data.rename(
    columns=dict(
        zip(
            st.columns.values, ["start_station_" + x.lower() for x in st.columns.values]
        )
    ),
    inplace=True,
)
data = data.merge(st, left_on="end_station_code", right_on="Code")
data.rename(
    columns=dict(
        zip(st.columns.values, ["end_station_" + x.lower() for x in st.columns.values])
    ),
    inplace=True,
)
data = data.loc[:, ~data.columns.duplicated()]

data = data[
    (data.start_station_latitude != -1.0)
    & (data.end_station_latitude != -1.0)
]

# Group data by all start/end station combinations and add the trip count
# print("Aggregating trip data to status/end station combinations...")
# comb = (
#     data.groupby(
#         [
#             "start_station_code",
#             "start_station_latitude",
#             "start_station_longitude",
#             "end_station_code",
#             "end_station_latitude",
#             "end_station_longitude",
#         ]
#     )
#     .size()
#     .to_frame("count")
#     .reset_index()
#     .sort_values("count", ascending=False)
# )

# # Remove trips where same start/end status (likely not real trips or edge cases)
# routes = comb[(comb["start_station_code"] != comb["end_station_code"])].reset_index(
#     drop=True
# )

# Pull all the directions from API and store locally
# for i, row in routes.iloc[0:30000].iterrows():
#     print(f"Processing trip {i} of 30000")
#     start_coord = (row["start_station_latitude"], row["start_station_longitude"])
#     end_coord = (row["end_station_latitude"], row["end_station_longitude"])
#     start_station_code = int(row["start_station_code"])
#     end_station_code = int(row["end_station_code"])
#     if not os.path.exists(
#         f"../data/directions/{start_station_code}_{end_station_code}json"
#     ):
#         print("Downloading direction...")
#         geom = get_directions(
#             start_coord, end_coord, start_station_code, end_station_code
#         )

# Calculate how many frames needed
delta = datetime.timedelta(seconds=10)
cnt = (END_DATETIME - START_DATETIME) / delta
center = [data.start_station_latitude.mean(), data.start_station_longitude.mean()]

img = []

# Iterate over each timeframe
start_datetime = START_DATETIME
while start_datetime < END_DATETIME:
    current_datetime = start_datetime + delta
    curr = cnt - (END_DATETIME - current_datetime) / delta
    print(
        f"Processing frame {str(int(curr))} of {str(int(cnt))} ({str(int(curr/cnt*100))}%)",
        end='\r'
    )
    subset = data[
        (data.start_date <= start_datetime)
        & (data.end_date > current_datetime)
        & (data.start_station_code != data.end_station_code)
    ]
    subset["geometry"] = subset.apply(lambda row: get_json_geometry(row), axis=1)
    im = get_frame(subset, center, current_datetime)
    img.append(im)
    start_datetime = current_datetime

save_gif(img, "bixi.gif")
