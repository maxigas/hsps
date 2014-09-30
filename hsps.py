#!/usr/bin/python3
from requests import get
from bs4 import BeautifulSoup
from re import findall
from re import compile as regex
from datetime import datetime
from time import gmtime, strftime, sleep
from joblib import Parallel, delayed
import matplotlib as mat
import matplotlib.pyplot as plot
import matplotlib.pylab as lab
import numpy as np
import pickle

debug = True

# Sample data:
#urls = ('http://hackerspaces.org/w/index.php?title=Special:Ask&offset=100&limit=20&q=%5B%5BCategory%3AHackerspace%5D%5D&p=format%3Dbroadtable%2Fmainlabel%3DHackerspace&po=%3F%3DHackerspace%23%0A%3FCountry%0A%3FState%0A%3FCity%0A%3FWebsite%0A%3FDate+of+founding%0A%3FHackerspace+status%0A&sort=Country')

# Real data:
urls = ('http://hackerspaces.org/w/index.php?title=Special:Ask&offset=100&limit=500&q=%5B%5BCategory%3AHackerspace%5D%5D&p=format%3Dbroadtable%2Fmainlabel%3DHackerspace&po=%3F%3DHackerspace%23%0A%3FCountry%0A%3FState%0A%3FCity%0A%3FWebsite%0A%3FDate+of+founding%0A%3FHackerspace+status%0A&sort=Country',
'http://hackerspaces.org/w/index.php?title=Special:Ask&offset=600&limit=500&q=%5B%5BCategory%3AHackerspace%5D%5D&p=format%3Dbroadtable%2Fmainlabel%3DHackerspace&po=%3F%3DHackerspace%23%0A%3FCountry%0A%3FState%0A%3FCity%0A%3FWebsite%0A%3FDate+of+founding%0A%3FHackerspace+status%0A&sort=Country')

def bug(s,newline=True):
    "Print, but only if the environment variable 'debug' is true."
    if debug and newline:
            print(str(s))
    if debug and not newline:
            print(str(s),end="")

def hsps_domains(urls):
    "Accepts urls of the hackerspaces wiki and returns hackerspace domains."
    domains = []
    for url in urls:
        soup = BeautifulSoup(get(url).text)
        for a in soup.table('a'):
        # Alternative selector: class="Website smwtype_uri"
            if "http" in a.string:
                domain = a.get('href').replace('http://','').replace('https://','').replace('www.','').rstrip('/').replace('site=','')
                if '/' in domain:
                    domain = domain[0:domain.find('/')]
                if domain not in (
                        "facebook",
                        "google",
                        "blogspot",
                        "wordpress",
                        "tumblr",
                        "groups",
                        "twitter"
                ):
                    bug("ADD: " + domain)
                    domains.append(domain)
                else:
                    bug("REM: " + domain)
    bug("Passing domains: " + ''.join(domains))
    return domains

def hsps_dates(domains):
    "Accepts domains and returns their presumed registration date (not exact)."
    if len(domains) < 1:
        raise NameError('No arguments to hsps_dates')
    dates = []
    bug('Processing ' + str(len(domains)) + ' domains...')
    bug('Entering loops...')
    dates = Parallel(n_jobs=201, verbose=100)(delayed(domain_to_date)(domain) for domain in domains)
    dates = list(filter(None, dates)) # Remove cases with no date found.
    dates.sort()
    return (dates, domains)

def domain_to_date(domain):
    "Accepts a domain and returns a date based on DNS"
    # Assuptions about valid hackerspace domain registration dates:
    regex_for_whois_dates = regex(r'20[0-1][0-9]-[0-9]+-[0-9]+')
    date = None
    try:
        bug('.',newline=False)
        potential_dates = regex_for_whois_dates.findall(get('http://whoiz.herokuapp.com/lookup?url='+domain).text)
        if potential_dates: # True if we found any dates in the output.
            potential_dates = [ datetime.strptime(x,'%Y-%m-%d') for x in potential_dates ]
            # Creation date should be the earliest:
            date = (min(potential_dates))
            bug('!',newline=False)
    except:
        bug('X',newline=False)
    sleep(1)
    return date

def hsps_plot(dates, domains):
    "Accepts dates and domains, returns a scatterplot."
    bug('Dates are' + str(dates))
    bug('Domains are' + str(domains))
    # Cleaning data
    dates = list(filter(None, dates))
    bug('New dates are' + str(dates))
    xdata = mat.dates.date2num(dates)
    ydata = range(len(xdata))
    colours = np.linspace(0.1,0.9,num=len(xdata))
    plot.gca().xaxis.set_major_formatter(mat.dates.DateFormatter('%Y'))
    plot.scatter(xdata, ydata, c=colours, marker='o', s=500, alpha=.8)
    stamp = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
    for extension in ('png','svg','pdf'):
        lab.savefig('plot'+stamp+'.'+extension)
        lab.savefig('plot'+'.'+extension)
    return (dates, domains)

def hsps_plots(dates, domains, dates2, domains2):
    "Accepts two bunch of dates and domains, returns a scatterplot."
    xdata  = mat.dates.date2num(dates)
    xdata2 = mat.dates.date2num(dates2)
    ydata,ydata2 = range(len(xdata)), range(len(xdata2))
    colours, colours2 = np.linspace(0.1,0.9,num=len(xdata)), np.linspace(0.1,0.9,num=len(xdata2))
    plot.gca().xaxis.set_major_formatter(mat.dates.DateFormatter('%Y'))
    plot.scatter(xdata, ydata, c=colours, marker='o', s=500, alpha=.5)
    plot.scatter(xdata2, ydata2, c=colours2, marker='*', s=400, alpha=0.75)
    stamp = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
    for extension in ('png','svg','pdf'):
        lab.savefig('plot'+stamp+'.'+extension)
        lab.savefig('plot'+'.'+extension)
    return (dates, domains)

def hsps_pickle(dates,domains):
    pickle.dump(domains,open('domains.pic','wb'))
    pickle.dump(dates,open('dates.pic','wb'))
    print('New files: domains.pic, dates.pic, plot...{png,svg,pdf}')

def hsps_unpickle():
    return (pickle.load(open('dates.pic','rb')), pickle.load(open('domains.pic','rb')))

def parse_hacklab_dates(filename="hacklab.dates"):
    "Accepts a file name and returns list of date objects"
    dates = [ datetime.strptime(date, "%m/%d/%y\n") for date in list(open(filename,'r')) ]
    dates.sort()
    return dates

def parse_hacklab_domains(filename="hacklab.domains"):
    "Accept file name and returns list of date objects"
    return [ domain.strip() for domain in list(open(filename,'r')) ]

# We could write this maybe with lambda:
parse_hacklab_domains2 = lambda x: [ domain.strip() for domain in list(open(x,'r')) ]

# Production:
hsps_pickle(*hsps_plot(*hsps_dates(hsps_domains(urls))))
hsps_plots(*hsps_unpickle(), dates2=parse_hacklab_dates(), domains2=parse_hacklab_domains())

# Development:
# hsps_plot(*hsps_unpickle())
# print(parse_hacklab_dates(), parse_hacklab_domains())
# hsps_plots(parse_hacklab_dates(), parse_hacklab_domains())
# hsps_plots(*hsps_unpickle(), dates2=parse_hacklab_dates(), domains2=parse_hacklab_domains())
# hsps_plot(parse_hacklab_dates(), parse_hacklab_domains())
