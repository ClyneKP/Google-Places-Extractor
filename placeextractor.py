import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import requests, json, populartimes, time, math
import os
import sys
import glob
import moviepy.editor as mpy

# enter api key 
api_key = sys.argv[1] 

# Google F&B Type Tags: bakery, bar, cafe, restaurant (meal_takeaway and meal_delivery seem to be subsets of restaurant)
search_type = "food"

# The location to search near
location = "33.834312,-118.315724"

#radius in miles
radius = 4

# url variable store url 
url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?type=" + search_type + "&"
nexturl = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"  

# Note that by virtue of the progressive focused radial search, results for the entire radius will be incomplete;
# complete results will only be returned for a bounding sqaure that fits entirely within the radius.

#Geographic Math Functions

def MilestoMeters(miles):
    return miles*1609.344

# Distances are measured in miles.
# Longitudes and latitudes are measured in degrees.
# Earth is assumed to be perfectly spherical.
earth_radius = 3960.0
degrees_to_radians = math.pi/180.0
radians_to_degrees = 180.0/math.pi

def change_in_latitude(miles):
    # Given a distance north, return the change in latitude.
    return (miles/earth_radius)*radians_to_degrees

def change_in_longitude(latitude, miles):
    # Given a latitude and a distance west, return the change in longitude.
    # Find the radius of a circle around the earth at given latitude.
    r = earth_radius*math.cos(latitude*degrees_to_radians)
    return (miles/r)*radians_to_degrees

#Define how to move in which direction
northeast = [1,1]
northwest = [-1,1] 
southeast = [1,-1]
southwest = [-1,-1]
directions = [northeast,northwest,southeast,southwest]

def Attempt(y,i,var):
    try:
        new = y[i][var]
        return new 
    except KeyError:
        return "NA"
        
def fetch_places(y,i):
    name = y[i]['name']
    place_id = y[i]['place_id']
    status = Attempt(y,i,'business_status')
    lat = y[i]['geometry']['location']['lat']
    lng = y[i]['geometry']['location']['lng']
    types =''
    for type in y[i]['types']:
        types += type + ", "
    rating = Attempt(y,i,'rating')
    ratings_total = Attempt(y,i,'user_ratings_total')
    vicinity = y[i]['vicinity']
    price_level = Attempt(y,i,'price_level')
    placedata = [name,place_id,lat,lng,status,types, rating, ratings_total, vicinity, price_level]   
    estabs.append(placedata)

def findPoint(point, direction, hypotenuse):
    return gpd.GeoDataFrame(
    point, geometry=gpd.points_from_xy(point.longitude+(change_in_longitude(change_in_latitude(hypotenuse),hypotenuse)*direction[0]), point.latitude+(change_in_latitude(hypotenuse)*direction[1])))

def getIDs(location,radius,gdf):
    r = requests.get(url + 'location=' + location + '&radius=' + str(MilestoMeters(radius)) + '&key=' + api_key) 
    print(url + 'location=' + location + '&radius=' + str(MilestoMeters(radius)) + '&key=' + api_key)
    x = r.json()
    y = x['results']
    count.append("x")
    try:
        next_page_token = str(x['next_page_token'])
    except KeyError:
        next_page_token = 0
    for i in range(len(y)): 
        fetch_places(y,i)
    #time.sleep(2)
    if next_page_token != 0:
        for i in directions:
            if not os.path.exists(search_type):
                os.makedirs(search_type)
            fig = gdf.get_figure()
            fig.savefig(search_type + "/plot_" + str(len(count)) + ".png")
            NextPage(location,radius,gdf,i)

    if next_page_token == 0:
        print("Terminus")
    
def NextPage(x,y,z,ac):
    location = x.split(sep = ",")
    newl = pd.DataFrame([[float(location[1]),float(location[0])]])
    newl.columns = ["longitude","latitude"]
    #Find new radius
    Half = y/2
    hypotenuse = math.sqrt((Half**2)/2)
    halfpoint = findPoint(newl,ac,hypotenuse)
    buffer = halfpoint.buffer(change_in_latitude(Half), resolution=50)
    newbase = buffer.boundary.plot(ax=z, linewidth=.5, color='black')
    halfl = str(halfpoint.geometry.y[0]) + "," + str(halfpoint.geometry.x[0])
    getIDs(halfl,Half,newbase)

StartPoint = location.split(sep = ",")
newl = pd.DataFrame([[float(StartPoint[1]),float(StartPoint[0])]])
newl.columns = ["longitude","latitude"]

gdf = gpd.GeoDataFrame(
    newl, geometry=gpd.points_from_xy(newl.longitude, newl.latitude))

gdf_buffer = gdf.buffer(change_in_latitude(radius), resolution=50)

ax = gdf_buffer.boundary.plot(figsize=(10, 10), linewidth=.5, color='black')
ax.set_axis_off()
estabs = []
count = []
getIDs(location,radius,ax)

print("There were a total of " + str(len(count)) + " requests.")
cost = len(count)*.032


print("Approximate Cost: $" + str(cost))

estabs = pd.DataFrame(estabs)
estabs.columns = ["Name","ID","Latitude","Longitude","Status","Types","Rating","Rating_Total","Vicinity","Price_Level"]
estabs = estabs.drop_duplicates(subset='ID', keep='first', inplace=False)

#Move to specific type directory
os.chdir(search_type)

#Save List of Establishments
estabs.to_csv("NYC_" + search_type + ".csv")

#Make a GIF of images
fps = 65
gif_name = search_type + '_recursion_' + str(fps) +"fps"
file_list = glob.glob('*.png') # Get all the pngs in the current directory
list.sort(file_list, key=lambda x: int(x.split('_')[1].split('.png')[0])) # Sort the images by #, this may need to be tweaked for your use case
clip = mpy.ImageSequenceClip(file_list, fps=fps)
clip.write_gif('{}.gif'.format(gif_name), fps=fps)
