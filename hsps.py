#!/usr/bin/python3

from requests import get
from bs4 import BeautifulSoup
from subprocess import check_output as bash
from re import findall
from re import compile as regex
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib as mat
import numpy as np

# Sample data:
#urls = ['http://hackerspaces.org/w/index.php?title=Special:Ask&offset=100&limit=20&q=%5B%5BCategory%3AHackerspace%5D%5D&p=format%3Dbroadtable%2Fmainlabel%3DHackerspace&po=%3F%3DHackerspace%23%0A%3FCountry%0A%3FState%0A%3FCity%0A%3FWebsite%0A%3FDate+of+founding%0A%3FHackerspace+status%0A&sort=Country']

# Real data:
urls = ['http://hackerspaces.org/w/index.php?title=Special:Ask&offset=100&limit=500&q=%5B%5BCategory%3AHackerspace%5D%5D&p=format%3Dbroadtable%2Fmainlabel%3DHackerspace&po=%3F%3DHackerspace%23%0A%3FCountry%0A%3FState%0A%3FCity%0A%3FWebsite%0A%3FDate+of+founding%0A%3FHackerspace+status%0A&sort=Country',
'http://hackerspaces.org/w/index.php?title=Special:Ask&offset=600&limit=500&q=%5B%5BCategory%3AHackerspace%5D%5D&p=format%3Dbroadtable%2Fmainlabel%3DHackerspace&po=%3F%3DHackerspace%23%0A%3FCountry%0A%3FState%0A%3FCity%0A%3FWebsite%0A%3FDate+of+founding%0A%3FHackerspace+status%0A&sort=Country']

debug = True

def bug(s,newline=True):
    "Debug function: Acts like print but only if the environment variable called debug is true."
    if debug:
        if newline:
            print(s)
        else:
            print(s,end="")

domains = []
for url in urls:
    soup = BeautifulSoup(get(url).text)
    for a in soup.table('a'):    # Alternative selector: class="Website smwtype_uri"
        if "http" in a.string:
            domain = a.get('href').replace('http://','').replace('https://','').replace('www.','').rstrip('/').replace('site=','')
            if '/' in domain:
                bug('Before: ' + domain)
                domain = domain[0:domain.find('/')]
                bug('After: ' + domain)
            bug("Found: " + domain)
            if "facebook" and "google" and "blogspot" and "wordpress" and "tumblr" and "groups" and "twitter" not in domain: # TODO: get this as array from config
                bug("ADD: " + domain)
                domains.append(domain)
            else:
                bug("REM: " + domain)

bug(domains)
dates = []

regex_for_whois_dates = regex(r'20[0-1][0-9]-[0-9]+-[0-9]+')
dates = []
for domain in domains:
    try:
        # bug('Whois for domain ' + domain)
        # Alternatively:
        # http://whoiz.herokuapp.com/lookup?url=example.com 
        potential_dates = regex_for_whois_dates.findall(get('http://whoiz.herokuapp.com/lookup?url='+domain).text)
#        bug(potential_dates)
        bug('.',newline=False)
#        potential_dates = regex_for_whois_dates.findall(str(bash(['whois', domain])))
        if potential_dates: # True if we found any dates in the output.
            potential_dates = [ datetime.strptime(x,'%Y-%m-%d') for x in potential_dates ]
            # Creation date is the earliest:
            dates.append(min(potential_dates))
            bug('!',newline=False)
    except:
        bug('X',newline=False)
dates.sort()
print(dates)
places = range(len(dates))
print(places)
dates = mat.dates.date2num(dates)
colours = np.linspace(0.1,0.9,num=len(dates))
plt.gca().xaxis.set_major_formatter(mat.dates.DateFormatter('%Y'))
plt.scatter(dates, places, c=colours, marker='o', s=200, alpha=.5)
plt.show()

