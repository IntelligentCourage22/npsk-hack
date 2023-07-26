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
from django.utils.safestring import mark_safe

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

# views.py
import plotly.graph_objs as go
import plotly.express as px
from django.http import JsonResponse
from django.views import View
from plotly.subplots import make_subplots


def home(request):
    return render(request,'index.html')


def details(request):
    lat = request.POST.get('lat')
    long = request.POST.get('long')
    date = str(request.POST.get('date')).replace("T"," ")
    request.session["lat"] = lat
    request.session["long"] = long
    request.session["date"] = date
    print(date)
    print(lat,long)
    if lat and long and date:
        return HttpResponseRedirect("/plotly_graph/")
    return render(request,'details.html')


def find_star(request):
    if request.method == "POST":
        name = request.POST["name"]
        hip = request.POST["hip"]
        cons = request.POST["cons"]
    return render(request, 'star_details.html')

#matplotlib graph, no return value, contains hover logic
"""def sky_projection(date, lat, long) : 

    global df, nomralized_df, maxs, mins 

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
"""

def sky_projection(request):
    date = request.session["date"]
    lat = float(request.session["lat"])
    long = float(request.session["long"])
    max_magnitude = 3.0
    if request.method == 'POST':
        # Get the entered Hipparcos ID from POST data
        hip_id = request.POST.get('hip_id')
        print(hip_id)
        ct = star_details(int(hip_id))
        print(ct)

    global df, nomralized_df, maxs, mins 

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
    stars['star_index'] = range(len(stars))

    print(stars)

    # Create the Plotly scatter plot
    valid_magnitude = stars['magnitude'].astype(float)
    valid_magnitude = valid_magnitude.fillna(0)  # Replace NaN with 0 or any default value

    # Calculate the size of each star based on its magnitude
    stars['marker_size'] = 50 * 5 ** (valid_magnitude / -2.5)

    # Apply magnitude-based filtering
    bright_stars = stars.magnitude <= max_magnitude

    # Create a scatter trace for the stars with circular markers
    trace = go.Scatter(
        x=stars["x"][bright_stars],
        y=stars["y"][bright_stars],
        mode="markers",
        marker=dict(
            symbol="circle",
            size=stars['marker_size'][bright_stars],
            color="white",
            opacity=0.5,  # Set the opacity of the stars (adjust as needed)
            line=dict(width=0),
        ),
        hovertext=stars["star_index"][bright_stars].astype(str),  # Use 'star_index' column for hover text
        hoverinfo="text",  # Show only the hover text, not the default info
    )

    # Create the Plotly figure
    fig = go.Figure(trace)

    # Update layout and remove axis ticks and labels
    fig.update_layout(
        plot_bgcolor="black",
        paper_bgcolor="black",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1, 1],
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1, 1],
        ),
        title="Sky Projection",
        title_font=dict(size=16, color="white"),
    )

    # Convert the Plotly figure to JSON for rendering in the template
    graph_json = fig.to_json()
    #ctx = star_details(hip_id)
    

    return render(request, "plot.html", {"graph_json": mark_safe(graph_json)})




def find_star_hip(hip) : 
    return hip 

#feed return values of finding star funcitons to star_details() and hr_diag()
def find_star_name(name) : 

    global df, nomralized_df, maxs, mins 

    constellations = pd.read_csv("constellations.csv")
    constellations = constellations.set_index("full")
    const_dict = constellations.to_dict()
    #print(const_dict)
    new_df = df[df['name'].notna()]
    id = new_df[new_df['name'].str.contains(name)]
    if not id.empty : 
        return int(id["hip"])
    else : return False 

def find_star_data(ra, dec, dist, mag, lum, cons): 

    if lum : 
        lum = math.log(lum)
        lum = lum/(maxs[-1]-mins[-1])
    if ra : ra = (ra-mins[0])/(maxs[0]-mins[0])
    if dec : dec = (dec-mins[1])/(maxs[1]-mins[1])
    if dist : dist = (dist-mins[2])/(maxs[2]-mins[2])
    if mag : mag = (mag-mins[6])/(maxs[6]-mins[6])


    vals_dict_raw = {'ra' : ra, 'dist' : dist, 'lum' : lum, 'dec' : dec, 'mag': mag}
    vals_dict = {}
    for i, j in vals_dict_raw.items() : 
        if j  : 
            vals_dict[i] = j
        
    if cons : 
        cons_df = df[df["constellation"] == cons]
        good_ids = cons_df['id'].tolist()
        dotp_df = normalized_df.loc[good_ids]

    vals_arr = np.array(list(vals_dict.values()))
    normalized_ref_vec =  vals_arr / np.linalg.norm(vals_arr)
    keys_lst = list(vals_dict.keys()) 

    #take only those colums which are useful to us 
    dotp_df = normalized_df.loc[:, keys_lst]
    #dotp_df = dotp_df.dropna()
    #print(dotp_df)

    for k, v in vals_dict.items() : 
        range_col = ((v - 0.1), (v + 0.1))
        mask = dotp_df[k].between(*range_col)
        dotp_df = dotp_df[mask]

    index_lst = dotp_df.index.to_list()
    print(dotp_df)
    dot_plst = []
    for i in index_lst : 
        vector = dotp_df.loc[i]
        vector = vector.to_numpy()
        vector_norm = vector / np.linalg.norm(vector)
        cos_theta = np.dot(vector_norm, normalized_ref_vec)
        dot_plst.append(cos_theta)

    dotp_df['cos_theta'] = dot_plst
    dotp_df_sorted = dotp_df.sort_values(by='cos_theta', ascending=False)
    id_lst = dotp_df_sorted.index.to_list()
    hip_lst_raw = df.loc[id_lst, 'hip']
    hip_lst = []
    for i in hip_lst_raw : 
        try : 
            x = int(i)
            hip_lst.append(x)
        except : pass
    
    return hip_lst

def hr_diag(hip):

    global df, nomralized_df, maxs, mins 

    id = df.get_loc(hip)

    am=df._get_value(id,'absmag')
    bv=df._get_value(id,'ci')
#----initialise mega list
    x=[]
    y=[]
#----initialise graph
    fig = plt.figure(linewidth=0)
    fig.patch.set_facecolor('black')
    ax=plt.axes()
    ax.set_xlim(-1,3)
    ax.set_ylim(-5,20)
    ax.xaxis.label.set_color('w')
    ax.yaxis.label.set_color('w')
    ax.spines['bottom'].set_color('w')
    ax.spines['top'].set_color('w') 
    ax.spines['right'].set_color('w')
    ax.spines['left'].set_color('w')
    ax.tick_params(colors='w', which='both')
    ax.set_facecolor("#000000")
#----- use data and put in mega list
    for i in range(4999):
        absmag=df._get_value(i,'absmag')
        ci=df._get_value(i,'ci')
        x.append(ci)
        y.append(absmag)
#-------- plotting + making it look decent
    plt.grid()
    plt.plot(bv,am,"w",marker="o",markersize=6)
    plt.scatter(x,y,c=x,cmap='YlOrRd',s=0.05)
    plt.text(bv-0.25,am+0.75,"your star",fontdict=dict(color='#bdbdbd', alpha=1, size=7))
    ax.invert_yaxis()
    plt.title("H-R diagram")
    plt.ylabel("absolute magnitude")
    plt.xlabel("B-V value")
    plt.savefig('hr_diagram',pad_inches=0)

def star_details(hip): 
    
    global df, nomralized_df, maxs, mins 

    filtered_df = df[df['hip'] == hip]
    id = filtered_df.index[0]
    display = dict(df.iloc[id])
    NaN = np.nan
    #print(display)
    print(type(display['hip']))
    for i in display:
        if display[i] is np.nan:
            display[i] = None

    if type(display['hip']) is float:
        hip = display['hip']
        display['hip'] = int(hip)
    #if display['name'] is NaN:
        #name="not found"
    #imp data 

    name = display['name']

    ci = display['ci']
    temp = 4_600*((1/((0.92*ci)+1.7))+(1/((0.92*ci)+0.62)))+15.411887306085191
    temp_kelvin = temp.round(3)
    
    lum = display['lum']
    lum = lum.round(3)
    radius = ((5_778/temp)**2)*(1/lum)**0.5
    radius = radius.round(3)

    dist = display['dist']*3.26156
    dist = dist.round(3)

    righta = display['ra']
    hh = int(righta//1)
    mm = int(((righta-hh)*60)//1)
    ss = int(((((righta-hh)*60)-mm)*60)//1)
    dec = display['dec']
    constellation = display['constellation']

    vals = f"distance: {(dist)} LY\n\ntemperature(surface): {temp_kelvin}K     \n\nradius: {radius} Solar"
    print(vals)
    data=f"right ascension(J2000): {hh}hrs {mm}m {ss}s\n\ndeclination(J2000): {dec}       "
    print(data)

    #other data 

    spect = display['spect'].strip()
    return {"name" : name, "temp" : temp_kelvin, "lum" : lum, "spect": spect, "dist" : dist, "radius": radius, "right_asc" : (hh,mm,ss), "dec" : dec}