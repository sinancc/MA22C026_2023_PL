# -*- coding: utf-8 -*-
"""Overview of tools.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/167QSohkNszNknZa3hWAK8a4cDvAzSEIR
"""

#First we are importing modules and sub modules we need

# Commented out IPython magic to ensure Python compatibility.
!pip install gitpython
import pandas as pd
import os
from git.repo import Repo
import matplotlib.pyplot as plt
import geopandas as gpd
import urllib
import shutil
# %matplotlib inline

#we are loading data next

covidfolder = '../../data_external/covid19'

if os.path.isdir(covidfolder): # if repo exists, pull newest data
  repo = Repo(covidfolder)
  repo.remotes.origin.pull()
else: # otherwise, clone from remote
  repo = Repo.clone_from('https://github.com/CSSEGISandData/COVID-19.git', covidfolder)
datadir = repo.working_dir + '/csse_covid_19_data/csse_covid_19_daily_reports'

c = pd.read_csv(datadir+'/03-27-2020.csv')
#We us pandas to get covid data for 03/27/2020 from the csv file

c.head()
#first five rows

geo = gpd.points_from_xy(c['Long_'], c['Lat'])
gc = gpd.GeoDataFrame(c, geometry=geo)
gc.head()
#we are mapping the data using geopandas

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world.plot();
#we load a low resolution map

base = world.plot(alpha=0.3)
msz = 500 * gc['Confirmed'] / gc['Confirmed'].max()
gc.plot(ax=base, column='Confirmed', markersize=msz, alpha=0.7);
#identifying trouble spots

co = c[c['Province_State']=='Oregon']
#restricting to oregon

census_url = 'https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_county_500k.zip'
your_download_folder = '../../data_external'
if not os.path.isdir(your_download_folder):
   os.mkdir(your_download_folder)
us_county_file = your_download_folder + '/cb_2018_us_county_500k.zip'
 # download if the file doesn't already exist
if not os.path.isfile(us_county_file):
  with urllib.request.urlopen(census_url) as response,open(us_county_file, 'wb') as out_file:
     shutil.copyfileobj(response, out_file)
#using urlib to add a file

us_counties = gpd.read_file(f"zip://{us_county_file}")
us_counties.head()
#using geopandas to read zip file

ore = us_counties[us_counties['STATEFP']=='41']
ore.plot();
#fips code for oregon is 41,knowing this makes easier

ore = ore.astype({'GEOID': 'int64'}).rename(columns={'GEOID' : 'FIPS'})
co = co.astype({'FIPS': 'int64'})
orco = pd.merge(ore, co.iloc[:,:-1], on='FIPS')

# plot coloring counties by number of confirmed cases
fig, ax = plt.subplots(figsize=(12, 8))
orco.plot(ax=ax, column='Confirmed', legend=True, legend_kwds={'label': '# confimed cases', 'orientation':'horizontal'})
# label the counties for
for x,y,county in zip(orco['Long_'], orco['Lat'], orco['NAME']):
    ax.text(x, y, county, color='grey')
ax.set_title('Confirmed COVID-19 cases in Oregon as of March 27 2020')
ax.set_xlabel('Latitude'); ax.set_ylabel('Longitude');