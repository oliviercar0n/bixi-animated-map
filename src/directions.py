
import os
import json
import requests
from urllib.parse import quote


TOKEN = "###"

def get_json_geometry(row):
    s1 = str(int(row['start_station_code']))
    s2 = str(int(row['end_station_code']))
    fp = 'directions/%s_%s.json' % (s1,s2)
    if not os.path.exists(fp):
        start_coord = (row['start_station_latitude'], row['start_station_longitude'])
        end_coord = (row['end_station_latitude'],row['end_station_longitude'])
        get_directions(start_coord,end_coord,s1,s2)                                      
    with open(fp) as f:
        data = json.load(f)
    return data['routes'][0]['geometry']

def get_directions(c1,c2,s1,s2):
    #TODO: Change this awful quote functions
    coord = quote("%f,%f;%f,%f" % (c1[1],c1[0],c2[1],c2[0]))
    url = 'https://api.mapbox.com/directions/v5/mapbox/cycling/' 
    params = {
        'access_token': TOKEN,
        'steps': 'false',
        'alternatives': 'false',
        'geometries': 'polyline'
    }
    r = requests.get(url+coord,params=params)
    with open(f'../directions/{s1}_{s2}.json', 'w') as f:
        json.dump(r.json(), f)
    
    return r.json()['routes'][0]['geometry']