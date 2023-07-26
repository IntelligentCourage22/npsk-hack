from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages
from django.http import Http404
from .models import *
import requests
import json


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