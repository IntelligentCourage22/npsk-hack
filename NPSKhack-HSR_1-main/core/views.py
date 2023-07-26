from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages
from django.http import Http404
from .models import *
import requests
import json
import tkinter as tk
import pandas as pd
import numpy as np
import math 
import matplotlib.pyplot as plt
from PIL import Image,ImageTk
from datetime import datetime,timedelta
from pytz import utc
from skyfield.api import Star, load
from skyfield.data import hipparcos
from skyfield.projections import build_stereographic_projection

global df, nomralized_df, maxs, mins 
df = pd.read_csv(r"names_const_database.csv")
df['id']  = df['id'].astype(int)
df = df.set_index('id')
normalized_df = pd.read_csv("normalized_database.csv")
#first row of normalized_database has max value of each col and second row has min values (done in excel)
maxs = np.array(normalized_df.iloc[0])[1:]
mins = np.array(normalized_df.iloc[1])[1:]
normalized_df = normalized_df.drop(0)
normalized_df = normalized_df.drop(1)
normalized_df['id']  = normalized_df['id'].astype(int)
normalized_df = normalized_df.set_index('id')

def home(request):
    return render(request,'index.html')


def details(request):
    lat = request.POST.get('lat')
    long = request.POST.get('long')
    print(lat,long)
    return render(request,'details.html')

def star_details(request):
    date = request.POST.get('star')
    print(date)
    return render(request,'star_details.html')
    

def index(request) : 
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/'+ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)
    return [location_data["lat"],location_data["lon"]]

def sky_projection(date, lat, long) : 

    # de421 shows position of earth and sun in space
    eph = load('de421.bsp')

    # hipparcos dataset contains star location data
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)

    #self made-------------------------------------------------------------------------------------------
    ts = load.timescale() #used later for conversion to appropriate datatype
    time=(int(lat)*4) #minutes, 1 deg long = 4 mins
    dt = datetime.strptime(date, '%Y-%m-%d %H:%M') #converting date time string to datetime format
    hour=time//60 #getting hours from time
    minute=(time-int(time))*60 #getting mins from time
    if hour<0: #will be -ve for west longitudes, +ve for east longitudes
        dateutc=dt+timedelta(hours=hour,minutes=minute) #bc for west longitudes (i.e +ve longs), you add to get GMT
    else:
        dateutc=dt+timedelta(hours=(-1)*hour,minutes=(-1)*minute) #east longitudes you subtract to get GMT
    dateutc=dateutc.replace(tzinfo=utc) #converting to appropriate format
    t = ts.utc(dateutc) #getting seconds req by module

    earth = eph["earth"]

    if lat<0:
        ra=((long+360)/15)
    else:
        ra=long/15
    zenith = Star(ra_hours=ra, dec_degrees=lat)

    center = earth.at(t).observe(zenith)

    projection = build_stereographic_projection(center)
    field_of_view_degrees = 180.0
    starpos = earth.at(t).observe(Star.from_dataframe(stars))
    stars["x"], stars["y"] = projection(starpos)

    bright_stars = (stars.magnitude <= 3)
    magnitude = stars["magnitude"][bright_stars]
    xcoords=stars["x"][bright_stars].to_frame()
    ycoords=stars["y"][bright_stars].to_frame()
    xcoords_hip = xcoords.copy()
    xcoords_hip.reset_index(level=0, inplace=True, col_level=0, col_fill='hip')
    xcoords.reset_index(drop=True, inplace=True)
    ycoords.reset_index(drop=True, inplace=True)

    fig, ax = plt.subplots(figsize=(6,6))
        
    border = plt.Circle((0, 0), 1, color="#000000", fill=True)
    ax.add_patch(border)
    marker_size = 50 * 5 ** (magnitude / -2.5)
    sky=ax.scatter(stars["x"][bright_stars], stars["y"][bright_stars],
        s=marker_size, color="white", marker=".", linewidths=0, 
        zorder=2)
    for i in range(len(xcoords)):
        x=xcoords._get_value(i,"x")
        y=ycoords._get_value(i,"y")
        value=ax.annotate(i,(x+0.007,y-0.006))
        value.set_visible(False)

    #plt.title("Copy the number under your star!")

    #horizon = Circle((0, 0), radius=1, transform=ax.transData)
    #for col in ax.collections:
        #col.set_clip_path(horizon)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    plt.axis("off")
    
    annot = ax.annotate("", xy=(0,0), xytext=(20,20),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        pos = sky.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        hip = xcoords_hip.loc[xcoords_hip['x'] == pos[0], 'hip'].values[0]
        text = f"({hip})"
        annot.set_text(text)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = sky.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)
    plt.show()

def find_star_name(name) : 
    print("HELLO WORLD")
    