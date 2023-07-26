
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

#--------------------------------------------LOADING DATA--------------------------------------------------------------

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


#--------------------------------------------TOP LEVELS-------------------------------------------------------------
def top_lev1():
       
    top1 = tk.Toplevel(window)
    top1.title("what am i looking at")
    top1.config(bg="#000000")
    top1.geometry("1000x500")
    
    with load.open(hipparcos.URL) as stard:
        stars = hipparcos.load_dataframe(stard)
        
    #entry for location, time
    tit=tk.Label(top1,text="Enter location \nand date time data",font=("Star Jedi Logo Monoline",20),bg="#000000",\
                 bd=0,fg="#FFFFFF")
    tit.place(x=300,y=50)
    
    latlab=tk.Label(top1,text="enter latitude : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
    latlab.place(x=200,y=200)
    
    
    longlab=tk.Label(top1,text="enter longitude : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
    longlab.place(x=200,y=250)
    
    datelab=tk.Label(top1,text="date : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
    datelab.place(x=200,y=300)
    
    timelab=tk.Label(top1,text="time : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
    timelab.place(x=550,y=300)
    
    latit=tk.StringVar(top1)
    longit=tk.StringVar(top1)
    year=tk.StringVar()
    month=tk.StringVar()
    day=tk.StringVar()
    hh=tk.StringVar()
    mm=tk.StringVar()
    
    
    def skyvar():
        year1=int(year.get())
        month1=int(month.get())
        day1=int(day.get())
        latitude=float(latit.get())
        longitude=float(longit.get())
        hh1=int(hh.get())
        mm1=int(mm.get())
        datestring=f"{year1}-{month1}-{day1} {hh1}:{mm1}"
        top1.destroy()
        # de421 shows position of earth and sun in space
        eph = load('de421.bsp')

        # hipparcos dataset contains star location data
        with load.open(hipparcos.URL) as f:
            stars = hipparcos.load_dataframe(f)

        #self made-------------------------------------------------------------------------------------------
        ts = load.timescale() #used later for conversion to appropriate datatype
        time=(int(longitude)*4) #minutes, 1 deg long = 4 mins
        dt = datetime.strptime(datestring, '%Y-%m-%d %H:%M') #converting date time string to datetime format
        hour=time//60 #getting hours from time
        minute=(time-int(time))*60 #getting mins from time
        if hour<0: #will be -ve for west longitudes, +ve for east longitudes
            dateutc=dt+timedelta(hours=hour,minutes=minute) #bc for west longitudes (i.e +ve longs), you add to get GMT
        else:
            dateutc=dt+timedelta(hours=(-1)*hour,minutes=(-1)*minute) #east longitudes you subtract to get GMT
        dateutc=dateutc.replace(tzinfo=utc) #converting to appropriate format
        t = ts.utc(dateutc) #getting seconds req by module

        earth = eph["earth"]

        if longitude<0:
            ra=((longitude+360)/15)
        else:
            ra=longitude/15
        zenith = Star(ra_hours=ra, dec_degrees=latitude)

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
        
        
    lat=tk.Entry(top1,textvariable=latit,fg="#FFFFFF",bg="#242424",font=("Cascadia Mono ExtraLight",8),bd=0)
    lat.place(x=400,y=200)
    
    long=tk.Entry(top1,textvariable=longit,fg="#FFFFFF",bg="#242424",font=("Cascadia Mono ExtraLight",8),bd=0)
    long.place(x=400,y=250)
    
    yearop=[i for i in range(1996,2024)]
    monthop=[i for i in range(1,13)]
    

    yearmenu=tk.OptionMenu(top1,year,*yearop)
    year.set("year")
    yearmenu.config(bg="#000000",fg="#FFFFFF",font=("Cascadia Mono ExtraLight",8),bd=0,relief="flat",\
                    borderwidth=0,highlightthickness=0,activebackground="#47452f",activeforeground="#FFFFFF")
    yearmenu.place(x=200,y=350)
    yearmenu.config(bd=0)
    
    monthmenu=tk.OptionMenu(top1,month,*monthop)
    month.set("month")
    monthmenu.config(bg="#000000",fg="#FFFFFF",font=("Cascadia Mono ExtraLight",8),bd=0,relief="flat",\
                    borderwidth=0,highlightthickness=0,activebackground="#47452f",activeforeground="#FFFFFF")
    monthmenu.place(x=300,y=350)
    monthmenu.config(bd=0)
    
    dayop=[i for i in range(1,32)]
    daymenu=tk.OptionMenu(top1,day,*dayop)
    day.set("day")
    daymenu.config(bg="#000000",fg="#FFFFFF",font=("Cascadia Mono ExtraLight",8),bd=0,relief="flat",\
                    borderwidth=0,highlightthickness=0,activebackground="#47452f",activeforeground="#FFFFFF")
    daymenu.place(x=410,y=350)
    daymenu.config(bd=0)
    
    hhop=[i for i in range(0,25)]
    
    hhmenu=tk.OptionMenu(top1,hh,*hhop)
    hh.set("hour")
    hhmenu.config(bg="#000000",fg="#FFFFFF",font=("Cascadia Mono ExtraLight",8),bd=0,relief="flat",\
                    borderwidth=0,highlightthickness=0,activebackground="#47452f",activeforeground="#FFFFFF")
    hhmenu.place(x=550,y=350)
    
    mmop=[i for i in range(0,61)]
    mmmenu=tk.OptionMenu(top1,mm,*mmop)
    mm.set("mins")
    mmmenu.config(bg="#000000",fg="#FFFFFF",font=("Cascadia Mono ExtraLight",8),bd=0,relief="flat",\
                    borderwidth=0,highlightthickness=0,activebackground="#47452f",activeforeground="#FFFFFF")
    mmmenu.place(x=650,y=350)
    mmmenu.config(bd=0)
    
    submitbut=tk.Button(top1,text="Submit",bg="#87640c",activebackground="#ab7d0a",activeforeground="#FFFFFF",command=skyvar,\
                        font=("Cascadia Mono ExtraLight",8),bd=0,padx=3,pady=3,fg="#FFFFFF")
    submitbut.place(x=450,y=410)
    
    return (year,month,day,latit,longit)

    
def top_lev2():

    top2 = tk.Toplevel(window)
    top2.title("find star")
    top2.config(bg="#000000")
    top2.geometry('1000x500')
    sc=0.25
    tit=tk.Label(top2,text="Enter name or hip id",font=("Star Jedi Logo Monoline",20),bg="#000000",\
                 bd=0,fg="#FFFFFF")
    tit.place(x=300,y=75)
    
    namelab=tk.Label(top2,text="enter name : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
    namelab.place(x=350,y=200)

    hip_lab=tk.Label(top2,text="enter hip  : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
    hip_lab.place(x=350,y=250)

    name_in=tk.StringVar(top2)
    hip_in=tk.StringVar(top2)

    name_entry=tk.Entry(top2,textvariable=name_in,fg="#FFFFFF",bg="#242424",font=("Cascadia Mono ExtraLight",8),bd=0)
    name_entry.place(x=475,y=200)
    
    hip_entry=tk.Entry(top2,textvariable=hip_in,fg="#FFFFFF",bg="#242424",font=("Cascadia Mono ExtraLight",8),bd=0)
    hip_entry.place(x=475,y=250)

    
    def got_it() : 
        
        name = str(name_in.get())
        hip = str(hip_in.get())
        print(name, hip)
        if hip : 
            try : 
                hip = int(hip)
                print("ok")
                #call final star function 
                #star_page(hip)
            except : 
                print("invalid input")
        elif name : 
            constellations = pd.read_csv("constellations.csv")
            constellations = constellations.set_index("full")
            const_dict = constellations.to_dict()
            #print(const_dict)
            new_df = df[df['name'].notna()]
            id = new_df[new_df['name'].str.contains(name)]
            if not id.empty : 
                hip = int(id["hip"])
                #call final star function 
                # star_page(hip)
            else : 
                lst = name.split()
                cons = lst[-1]
                try : 
                    new_name = ' '.join(lst[:-1]) + ' ' +  const_dict[cons]
                    id = new_df[new_df['name'].str.contains(new_name)]
                    if not id.empty : 
                        print(int(id["hip"]))
                        #call final star function 
                    else : print("invalid")
                except : print('invalid')

    #starlist=[4958,47548,3848]
    def optionlist(starlist):

        hipval=tk.Toplevel(window)
        hipval.title("choose")
        hipval.config(bg="#000000")
        hipval.geometry("400x200")
        def getval():
            hipvalue=int(star.get())
            print(hipvalue)
            #star_page(hip)
        
        if len(starlist) == 0 : 
            tit=tk.Label(hipval,text="Invalid Values",font=("Star Jedi Logo Monoline",15),bg="#000000",\
                        bd=0,fg="#FFFFFF")
            tit.place(x=65,y=20)
        
        if len(starlist) > 5 : 
            starlist = starlist[:5]
            
        tit=tk.Label(hipval,text="Select hip value\nof star you wanna see",font=("Star Jedi Logo Monoline",15),bg="#000000",\
                        bd=0,fg="#FFFFFF")
        tit.place(x=65,y=20)
        star=tk.StringVar(hipval)
        starmenu=tk.OptionMenu(hipval,star,*starlist)
        star.set("choose hip value")
        starmenu.config(bg="#000000",fg="#FFFFFF",font=("Cascadia Mono ExtraLight",8),bd=0,relief="flat",\
                            borderwidth=0,highlightthickness=0,activebackground="#47452f",activeforeground="#FFFFFF")
        starmenu.place(x=130,y=105)
        submitbut=tk.Button(hipval,text="Submit",bg="#87640c",activebackground="#ab7d0a",activeforeground="#FFFFFF",command=getval,\
                                font=("Cascadia Mono ExtraLight",8),bd=0,padx=3,pady=3,fg="#FFFFFF")
        submitbut.place(x=175,y=150)
        hipval.mainloop()

    def top_entry_vals() : 
        entry_win = tk.Toplevel(window)
        entry_win.title("enter values")
        entry_win.geometry("700x700")
        entry_win.config(bg="#000000")
        top2.destroy()
        tit=tk.Label(entry_win,text="enter some or all\nof these values",font=("Star Jedi Logo Monoline",20),bg="#000000",\
                 bd=0,fg="#FFFFFF")
        tit.place(x=115,y=50)

        ra_in = tk.StringVar(entry_win)
        dec_in = tk.StringVar(entry_win)
        dist_in = tk.StringVar(entry_win)
        mag_in = tk.StringVar(entry_win)
        spect_in = tk.StringVar(entry_win)
        lum_in = tk.StringVar(entry_win)
        cons_in = tk.StringVar(entry_win)

        # ra 
        ra_lab=tk.Label(entry_win,text="enter J2000 ra : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
        ra_lab.place(x=115,y=200)

        ra_entry=tk.Entry(entry_win,textvariable=ra_in,fg="#FFFFFF",bg="#242424",font=("Cascadia Mono ExtraLight",8),bd=0)
        ra_entry.place(x=250,y=200)

        # dec
        dec_lab=tk.Label(entry_win,text="enter J2000 dec : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
        dec_lab.place(x=115,y=250)

        dec_entry=tk.Entry(entry_win,textvariable=dec_in,fg="#FFFFFF",bg="#242424",font=("Cascadia Mono ExtraLight",8),bd=0)
        dec_entry.place(x=250,y=250)

        #dist 
        dist_lab=tk.Label(entry_win,text="enter dist : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
        dist_lab.place(x=115,y=300)

        dist_entry=tk.Entry(entry_win,textvariable=dist_in,fg="#FFFFFF",bg="#242424",font=("Cascadia Mono ExtraLight",8),bd=0)
        dist_entry.place(x=250,y=300)

        #mag 
        mag_lab=tk.Label(entry_win,text="enter mag : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
        mag_lab.place(x=115,y=350)

        mag_entry=tk.Entry(entry_win,textvariable=mag_in,fg="#FFFFFF",bg="#242424",font=("Cascadia Mono ExtraLight",8),bd=0)
        mag_entry.place(x=250,y=350)

        #spect 
        '''
        spect_lab=tk.Label(entry_win,text="enter spect : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
        spect_lab.place(x=115,y=400)

        spect_entry=tk.Entry(entry_win,textvariable=spect_in,fg="#FFFFFF",bg="#242424",font=("Cascadia Mono ExtraLight",8),bd=0)
        spect_entry.place(x=250,y=400)
        '''

        #lum 
        lum_lab=tk.Label(entry_win,text="enter lum : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
        lum_lab.place(x=115,y=400)

        lum_entry=tk.Entry(entry_win,textvariable=lum_in,fg="#FFFFFF",bg="#242424",font=("Cascadia Mono ExtraLight",8),bd=0)
        lum_entry.place(x=250,y=400)

        #cons 
        cons_lab=tk.Label(entry_win,text="enter cons : ",fg="#FFFFFF",bg="#000000",font=("Cascadia Mono ExtraLight",8),bd=0)
        cons_lab.place(x=115,y=450)

        cons_entry=tk.Entry(entry_win,textvariable=cons_in,fg="#FFFFFF",bg="#242424",font=("Cascadia Mono ExtraLight",8),bd=0)
        cons_entry.place(x=250,y=450)

        
        def search_algo() : 
            #get input for certain values and then scale them using maxs and mins to make vals_dict
            #since lum values are so varied, take log e before normalizing input value
            ra, dec, dist, mag, lum, cons = float(ra_in.get()), float(dec_in.get()), float(dist_in.get()), float(mag_in.get()), float(lum_in.get()), str(cons_in.get())
            
            if lum != -100: 
                lum = math.log(lum)
                lum = lum/(maxs[-1]-mins[-1])
            if ra != -100 : ra = (ra-mins[0])/(maxs[0]-mins[0])
            if dec != -100 : dec = (dec-mins[1])/(maxs[1]-mins[1])
            if dist != -100 : dist = (dist-mins[2])/(maxs[2]-mins[2])
            if mag != -100 : mag = (mag-mins[6])/(maxs[6]-mins[6])

            print(ra, dec, dist, mag, lum, cons)

            vals_dict_raw = {'ra' : ra, 'dist' : dist, 'lum' : lum, 'dec' : dec, 'mag': mag}
            vals_dict = {}
            for i, j in vals_dict_raw.items() : 
                if j != -100 : 
                    vals_dict[i] = j
                
            if cons != '-100' : 
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
            optionlist(hip_lst)

        submitbut=tk.Button(entry_win,text="Submit",bg="#87640c",activebackground="#ab7d0a",activeforeground="#FFFFFF",command=search_algo,
                        font=("Cascadia Mono ExtraLight",8),bd=0,padx=3,pady=3,fg="#FFFFFF")
        submitbut.place(x=275,y=550)

        footer=tk.Label(entry_win,text="if you dont have\nany of the \nfollowing\nvalues, enter -100",font=("Cascadia Mono ExtraLight",8),bg="#121212",\
                        fg="#FFFFFF",padx=20,pady=20)
        footer.place(x=475,y=250)

        
        return (ra_in, dec_in, dist_in, mag_in, spect_in, lum_in, cons_in)

    submitbut=tk.Button(top2,text="Submit",bg="#87640c",activebackground="#ab7d0a",activeforeground="#FFFFFF",command=got_it,\
                        font=("Cascadia Mono ExtraLight",8),bd=0,padx=3,pady=3,fg="#FFFFFF")
    submitbut.place(x=550,y=350)

    get_vals_but=tk.Button(top2,text="Dont have values",bg="#87640c",activebackground="#ab7d0a",activeforeground="#FFFFFF",       command=top_entry_vals,\
                        font=("Cascadia Mono ExtraLight",8),bd=0,padx=3,pady=3,fg="#FFFFFF")
    get_vals_but.place(x=350,y=350)

    return(name_in, hip_in)



def top_lev3():
    top3 = tk.Toplevel(window)
    top3.title("tutorial")
    top3.geometry("500x500")
    top3.config(bg="#000000")
    
#--------------------FUNCTIONALITIES-----------------------------------------------------------------------------------
  
def star_page(hip) :

    def hr_diag():
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
        plt.savefig('temp',pad_inches=0)
    #--------placing the figure
        im = Image.open("temp.png")
        im=im.resize((320,240))
        ph = ImageTk.PhotoImage(im)
        hr=tk.LabelFrame(window,text="        ☾⋆°• hr diagram •°⋆☽",height=300,width=250,\
                    fg="#FFFFFF",bg="#121212",relief="flat",font=("Cascadia Mono ExtraLight",8),padx=5,pady=10)
        hr.place(x=500,y=100)
        hrbut=tk.Button(hr,image=ph,bd=0,relief="flat",bg="#000000",activebackground="#000000")
        hrbut.image=ph
        hrbut.pack()



#look = ImageTk.PhotoImage(Image.open("_look.png")) 
#find=tk.Button(window,image=look,bd=0)
#find.place(x=150,y=250)

#----------------------------------MAIN WINDOW-------------------------------------------------------------------------

# --- WINDOW 
window=tk.Tk()
window.title("stars")
window.config(bg="#000000")
window.geometry("1000x467")
bg=tk.PhotoImage(file="bg.png")
label1=tk.Label(window,image=bg)
label1.place(x=0,y=0)
 # --- BUTTONS
look=tk.Button(window,text="what am i looking at",bg="#000000",fg="#FFFFFF",activebackground="#524626", activeforeground="#FFFFFF",\
               borderwidth=0.1,bd=0.1,font=("Cascadia Mono ExtraLight",8),padx=20,pady=20,command=top_lev1)
look.place(x=100,y=250)
find=tk.Button(window,text="find star",bg="#000000",fg="#FFFFFF",activebackground="#524626", activeforeground="#FFFFFF",\
               borderwidth=0.1,bd=0.1,font=("Cascadia Mono ExtraLight",8),padx=20,pady=20,command=top_lev2)
find.place(x=450,y=250)
tutorial=tk.Button(window,text="tutorial",bg="#000000",fg="#FFFFFF",activebackground="#524626", activeforeground="#FFFFFF",\
               borderwidth=0.1,bd=0.1,font=("Cascadia Mono ExtraLight",8),padx=20,pady=20,command=top_lev3)
tutorial.place(x=725,y=250)

#--------------------------------------??END??------------------------------------------------------------------
window.mainloop()



# features to add
# if cos theta < 0.98 no match
# if cos theta < 1 and 1 is unique, then first star is match and 3 follow ups are possibilities 
# if cos theta = 1 then first star is match and could be any of following 1s 
# tutorial within tkinter
# robusting
# object oriented programming 