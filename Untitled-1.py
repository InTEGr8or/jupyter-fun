# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %% [markdown]
# <a href="https://colab.research.google.com/github/InTEGr8or/jupyter-fun/blob/master/nCov2019.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
# %% [markdown]
# # Infection Rates per day
#
# %% [markdown]
# ## Purpose and Source
#
# [this code available on Github](https://github.com/InTEGr8or/jupyter-fun/blob/master/nCov19.ipynb)
#
# The percent rates in the sheet at the bottom are approximations. Data seems to be released about twice a day. Sometimes there is a lag, and they release it at different times.
#
# Optimally, the time of the update would be taken into account and prorated per hour and multiplied by the number of hours difference but I am just starting to learn Python so there are probably a lot of improvements that could be made.
#
# Data is collected by Johns Hopkins in Baltimore and published here: [nCov19 contagion](https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6)
#
# Here is another excellent data presentation at [WorldOMeters.info](https://www.worldometers.info/coronavirus/#repro)
#
# Now a [Time Series Table](https://docs.google.com/spreadsheets/u/1/d/1UF2pSkFTURko2OvfHWWlFpDFAr1UxCBA4JLwlSP6KFo/htmlview?usp=sharing&sle=true) is available, and a [Feature Layers](https://gisanddata.maps.arcgis.com/home/item.html?id=c0b356e20b30490c8b8b4c7bb9554e7c) appears to be available but it requires authentication.
#
# The single-sheet Time Series is a much cleaner data source and _doesn't require repeated reauthentication_ so I'm reworking it to use that and we don't have a percent change right now, until I figure out how to use Pandas properly.
#
# ## This first section sets up the imports and some parsing functions.
#

# %%
try:
  from bs4 import BeautifulSoup
except:
  get_ipython().system('pip install beautifulsoup4')
  from bs4 import BeautifulSoup

import requests
import numpy as np
from dateutil import parser
from datetime import datetime
import pandas as pd

tsc_csv = "https://docs.google.com/spreadsheets/u/1/d/1UF2pSkFTURko2OvfHWWlFpDFAr1UxCBA4JLwlSP6KFo/export?format=csv"
tsc_html = "https://docs.google.com/spreadsheets/u/1/d/1UF2pSkFTURko2OvfHWWlFpDFAr1UxCBA4JLwlSP6KFo/htmlview?usp=sharing&sle=true#"

pd.set_option('display.max_rows', 200)

states = {
  'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AS': 'American Samoa',
  'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut',
  'DC': 'District of Columbia', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
  'GU': 'Guam', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois',
  'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts',
  'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota',
  'MO': 'Missouri', 'MP': 'Northern Mariana Islands', 'MS': 'Mississippi',
  'MT': 'Montana', 'NA': 'National',
  'NC': 'North Carolina',
  'ND': 'North Dakota',
  'NE': 'Nebraska',
  'NH': 'New Hampshire',
  'NJ': 'New Jersey',
  'NM': 'New Mexico',
  'NV': 'Nevada',
  'NY': 'New York',
  'OH': 'Ohio',
  'OK': 'Oklahoma',
  'OR': 'Oregon',
  'PA': 'Pennsylvania',
  'PR': 'Puerto Rico',
  'RI': 'Rhode Island',
  'SC': 'South Carolina',
  'SD': 'South Dakota',
  'TN': 'Tennessee',
  'TX': 'Texas',
  'UT': 'Utah',
  'VA': 'Virginia',
  'VI': 'Virgin Islands',
  'VT': 'Vermont',
  'WA': 'Washington',
  'WI': 'Wisconsin',
  'WV': 'West Virginia',
  'WY': 'Wyoming',
  'AB': 'Alberta',
  'BC': 'British Columbia',
  'MB': 'Manitoba',
  'NB': 'New Brunswick',
  'NL': 'Newfoundland and Labrador',
  'NT': 'Northwest Territories',
  'NS': 'Nova Scotia',
  'NU': 'Nunavut',
  'ON': 'Ontario',
  'PE': 'Prince Edward Island',
  'QC': 'Quebec',
  'SK': 'Saskatchewan',
  'YT': 'Yukon'
}

def is_date(text):
  try:
    s = parser.parse(text)
    return True
  except:
    return False

def hotten(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    if '%' in s:
      # print(s)
      is_max = float(s.replace('%', '')) > 20
      return ['background-color: yellow' if v else '' for v in is_max]
    else:
      return 'background-color: black'

def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    heat = str(hex(min(int(val.replace('%', '')) * 10 + 56, 255))).split('x')[-1].upper()
    color = f'#{heat}5555'
    # print(val, heat, color)
    return 'color: %s' % color


# %%
dft = pd.read_csv(tsc_csv)
dft.rename(columns={'2/8/20 10:24': '2/8/2020 10:24 AM'}, inplace=True)

dates = [col for i, col in enumerate(dft.columns) if is_date(col) ]
dates.reverse()

dfr = pd.read_csv(tsc_csv + "&gid=1940183135")
dfm = pd.read_csv(tsc_csv + "&gid=1056055583")
dfm.rename(columns={'Country/Region': 'Country', 'Province/State': 'State'}, inplace=True)
dfm['Country'].replace('Mainland China','China', inplace=True)

# Get date of first death or days since first death.
for i, row in dfm.iterrows():
  mdates = [col for i, col in enumerate(dft.columns) if is_date(col)]
  for date in mdates:
    if row[date] > 0:
      # print('Death Date:', row['Country'], row['State'], date, row)
      row['First Death Date'] = date

dfm.apply
dfm.set_index(['Country', 'State'], inplace=True)
dft.fillna('')
df = pd.DataFrame()


# Get tabs from Html
page = requests.get(tsc_html)
bs = BeautifulSoup(page.text)
tpath = "//div[@id='sheets-viewport']/div //table"
tables = bs.select('div#sheets-viewport div table')
trc = tables[0].select("tr")
th = trc[0].select('th')

# First confirmed date in country (Est.)
df['Country'] = dft['Country/Region'].replace('Mainland China', 'China').replace('United Arab Emirates', 'UAE')
df['State'] = dft['Province/State'].fillna('')
# df.set_index(['Country', 'State'], inplace=True)
df['First Case'] = dft['First confirmed date in country (Est.)']
df['Days Ago'] = datetime.now() - df['First Case'].apply(lambda date: parser.parse(date, fuzzy=True))
df['Days Ago'] = df['Days Ago'].apply(lambda days: str(days).split(' ')[0])
df['Death Toll'] = 0
for i, row in df.iterrows():
  country = row['Country']
  state = row['State']
  today = dates[0]
  if ',' in state:
    # print(row['State'], states[row['State'].split(',')[1].strip()])
  if row['State'] == '':
    try:
      mrow = dfm.loc[country, today]
      if 'Phil' in country:
        print('Phil:', country, type(country))
        print('Phil', mrow[0])
    except:
      mrow = 0
  else:
    try:
      mrow = dfm.loc[country, :].loc[state.split(',')[0], dates[0]]
    except:
      print("ERROR:", country, state, type(state))
      mrow = 0
  if isinstance(mrow, (int, float, complex)) and not isinstance(mrow, bool):
    if mrow > 0:
      # print(row['Country'], row['State'], mrow)
      df.at[i, 'Death Toll'] = mrow

# Remove early results
for i, date in enumerate(dates):
  if i < len(dates) -1 and parser.parse(date).day == parser.parse(dates[i + 1]).day:
    del dates[i + 1]
# Append to columns
percents = []
for i, date in enumerate(dates):
  d = parser.parse(date)
  col = d.strftime('%B')[:3] + d.strftime('%d')
  df[col] = dft[date].replace(np.inf, 0).fillna(0).astype(int)
  if i < len(dates) - 1:
    pcol = dates[i + 1]
    percents.append(col + '%')
    df[col + '%'] = round((dft[date] / dft[dates[i + 1]].fillna(0) * 100) - 100).replace(np.inf, 0).fillna(0).astype(int).astype(str) + '%'

# %% [markdown]
# ## Render

# %%
# df.set_index('Country', inplace=True)
df.drop(columns=['First Case']).sort_values(by=['Country','State'], ascending=[True, True]).style.applymap(color_negative_red, subset=percents)

