"""Further GUI"""

hip=657
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image,ImageTk
import math
import numpy as np

def hr_diag(id,df):
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

df=pd.read_csv('names_const_database.csv')

#id=df.get_loc(hip)
id = 55
window=tk.Tk()
window.title("stars")
window.config(bg="#000000")
window.geometry("1000x600")
label1=tk.Label(window,text="about",bg="#000000",fg="#FFFFFF",\
               borderwidth=0.1,bd=0.1,font=("Star Jedi Logo MonoLine",25),padx=10,pady=0)
label1.place(x=30,y=10)

display=dict(df.iloc[id])
NaN=np.nan
#print(display)
print(type(display['hip']))
for i in display:
    if display[i] is np.nan:
        display[i]="not found"

if type(display['hip']) is float:
    hip=display['hip']
    display['hip']=int(hip)
#if display['name'] is NaN:
    #name="not found"

label2=tk.Label(window,text=f"(hipparcos id: {display['hip']}; name: {display['name']})",bg="#000000",fg="#FFFFFF",font=("Cascadia Mono ExtraLight",8),bd=0)
label2.place(x=225,y=39)


ci=display['ci']
temp=4_600*((1/((0.92*ci)+1.7))+(1/((0.92*ci)+0.62)))+15.411887306085191
lum=display['lum']
radius=((5_778/temp)**2)*(1/lum)**0.5
temp=temp.round(3)
vals=f"distance: {(display['dist']*3.26156).round(3)} LY\n\ntemperature(surface): {temp.round(3)}K     \n\nradius: {radius.round(3)} Solar"
print(vals)

gen=tk.LabelFrame(window,text="       ☾⋆°• general info •°⋆☽",height=300,width=250,\
                  fg="#FFFFFF",bg="#121212",relief="flat",font=("Cascadia Mono ExtraLight",8),padx=5,pady=10)
gen.place(x=120,y=100)
label1=tk.Label(gen,text=vals,bg="#000000",fg="#FFFFFF",font=("Cascadia Mono ExtraLight",8))
label1.pack()
hr_diag(id,df)

loc=tk.LabelFrame(window,text="      ☾⋆°• location data •°⋆☽",height=300,width=250,\
                  fg="#FFFFFF",bg="#121212",relief="flat",font=("Cascadia Mono ExtraLight",8),padx=5,pady=10)
loc.place(x=120,y=260)
righta=display['ra']
hh=int(righta//1)
mm=int(((righta-hh)*60)//1)
ss=int(((((righta-hh)*60)-mm)*60)//1)
data=f"right ascension(J2000): {hh}hrs {mm}m {ss}s\n\ndeclination(J2000): {display['dec']}       "
print(data)
label2=tk.Label(loc,text=data,bg="#000000",fg="#FFFFFF",font=("Cascadia Mono ExtraLight",8))
label2.pack()

constellation=tk.Label(window,text="constellation: ")
constellation.place(x=120,y=350)
#comp, comp primary, lum, const
#print(display)
"""NaN=np.nan
display.replace(NaN,"none found")
disp=display.to_string(na_rep='none found')
print(type(disp))
label2=tk.Label(window,text=disp[:504])
label2.place(x=100,y=20)
label3=tk.Label(window,text=disp[505:])
label3.place(x=300,y=20)"""
window.mainloop()