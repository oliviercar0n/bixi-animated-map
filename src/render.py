import io
import folium
import polyline
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from datetime import datetime
from geometry import get_waypoint

def save_gif(img_list: list):

    cropped_images = []
    for i in img_list:
        width, height = i.size 
        cropped_images.append(i.crop((0,75,width-200,height-20)))

    cropped_images[0].save('bixi.gif',save_all=True,append_images=cropped_images[1:], duration = 40, loop=0)
    
def get_frame(bike_data:pd.DataFrame, center, timestamp:datetime):

    m = folium.Map(
        location = center,
        zoom_start = 12,
        tiles = "CartoDB dark_matter"
    )

    for i, row in bike_data.iterrows():
        if row['geometry'] is not None:
            coord = polyline.decode(row['geometry'])
            dur = (row['end_date'] - row['start_date']).seconds
            ela = (timestamp - row['start_date']).seconds
            factor = float(ela/dur)
            xys = get_waypoint(coord,factor)['path']
            folium.PolyLine(
                xys,
                opacity = 0.7, 
                smoothFactor = 3,
                weight = 1,
            ).add_to(m)

    for i, row in bike_data.iterrows():
        if row['geometry'] is not None:
            coord = polyline.decode(row['geometry'])
            dur = (row['end_date'] - row['start_date']).seconds
            ela = (timestamp - row['start_date']).seconds
            factor = float(ela/dur)
            x,y = get_waypoint(coord,factor)['waypoint']

            folium.Circle([x,y], radius = 0.01, color = 'white' ,opacity = 1,).add_to(m)
    
    im = Image.open(io.BytesIO(m._to_png()))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype('Roboto-BoldCondensed.ttf',25)
    draw.text((50, 125),str(timestamp),(255,255,255),font=font)
    
    return im