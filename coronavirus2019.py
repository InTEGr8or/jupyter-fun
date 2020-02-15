# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %% [markdown]
# <a href="https://colab.research.google.com/github/InTEGr8or/jupyter-fun/blob/master/nCov2019.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

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

tsc_csv = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
tsm_csv = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
tsr_csv = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"

def day_tot(day):
  return f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{day.strftime('%m-%d-%Y')}.csv"

pd.set_option('display.max_rows', 200)

states = {
  'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AS': 'American Samoa',
  'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut',
  'DC': 'District of Columbia', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
  'GU': 'Guam', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois',
  'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts',
  'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota',
  'MO': 'Missouri', 'MP': 'Northern Mariana Islands', 'MS': 'Mississippi',
  'MT': 'Montana', 'NA': 'National', 'NC': 'North Carolina', 'ND': 'North Dakota',
  'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
  'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon',
  'PA': 'Pennsylvania', 'PR': 'Puerto Rico', 'RI': 'Rhode Island', 'SC': 'South Carolina',
  'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
  'VA': 'Virginia', 'VI': 'Virgin Islands', 'VT': 'Vermont', 'WA': 'Washington',
  'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming', 'AB': 'Alberta',
  'BC': 'British Columbia', 'MB': 'Manitoba', 'NB': 'New Brunswick',
  'NL': 'Newfoundland and Labrador', 'NT': 'Northwest Territories',
  'NS': 'Nova Scotia', 'NU': 'Nunavut', 'ON': 'Ontario', 'PE': 'Prince Edward Island',
  'QC': 'Quebec', 'SK': 'Saskatchewan', 'YT': 'Yukon'
}

def update_firsts(df, firsts_col):
  # Get date of first death or days since first death.
  df[firsts_col] = ''
  dates = [col for col in df.columns if is_date(col) ]
  for i, row in df.iterrows():
    for date in dates:
      try:
        if row[date] != None and row[date] > 0:
          df.at[i, firsts_col] = 'updated'
          # print(f"update_firsts(df, {firsts_col}):\n", date, row[date])
      except:
        print(f"### ERROR update_firsts(df, {firsts_col}):\n", i)
  print(f"{firsts_col}\n", df)
  return df

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
dates = [col for i, col in enumerate(dft.columns) if is_date(col) ]
dates.reverse()

dfr = pd.read_csv(tsr_csv)
dfm = pd.read_csv(tsm_csv)
dfm.rename(columns={'Country/Region': 'Country', 'Province/State': 'State'}, inplace=True)
dfm['Country'].replace('Mainland China','China', inplace=True)
mdates = [col for i, col in enumerate(dfm.columns) if is_date(col)]

# Get date of first death or days since first death.
dfm = update_firsts(dfm, 'First Death')

dfm.set_index(['Country', 'State'], inplace=True)
dft.fillna('')
dfm.fillna('')
df = pd.DataFrame()

df['Country'] = dft['Country/Region'].replace('Mainland China', 'China').replace('United Arab Emirates', 'UAE')
df['State'] = dft['Province/State'].fillna('')
# df.set_index(['Country', 'State'], inplace=True)
df['Death Toll'] = 0
df['Death Aging'] = 0

df = update_firsts(df, 'First Confirmed')
df
# df['Confirmed Aging'] = datetime.now() - df['First Case'].apply(lambda date: parser.parse(date, fuzzy=True))
# df['Confirmed Aging'] = df['Confirmed Aging'].apply(lambda days: str(days).split(' ')[0])
# df.drop(columns=['First Case'], inplace=True)
# df.sort_values(by=['Country','State'], ascending=[True, True], inplace=True)
# today = dates[0]
# mtoday = mdates[-1]
# print("Latest sheet dates:", today, mtoday)
# for i, row in df.iterrows():
#   country = row['Country']
#   state = row['State']
#   locality = ''
#   ### They've cleaned up their join columns a bit.
#   # if ',' in state:
#   #   locality = state.split(',')[0].strip()
#   #   state = states[state.split(',')[1].strip()]
#   if state == '' or state == 'NaN':
#     try:
#       mrow = dfm.loc[country, mtoday]
#       if 'Phil' in country:
#         # print('Phil:', country, type(country))
#         # print('Phil', mrow[0])
#         mrow = mrow[0]
#     except:
#       mrow = 0
#   else:
#     try:
#       mrow = dfm.loc[country, :].loc[state, mtoday]
#     except:
#       print("ERROR:", country, state, type(state))
#       mrow = 0
#   if isinstance(mrow, (int, float, complex)) and not isinstance(mrow, bool):
#     if mrow > 0:
#       print(row['Country'], row['State'], mrow)
#       df.at[i, 'Death Toll'] = mrow
# print(dfm[mtoday])
# # Remove early results
# for i, date in enumerate(dates):
#   if i < len(dates) -1 and parser.parse(date).day == parser.parse(dates[i + 1]).day:
#     del dates[i + 1]
# # Append to columns
percents = []
for i, date in enumerate(dates):
  d = parser.parse(date)
  col = d.strftime('%B')[:3] + d.strftime('%d')
  df[col] = dft[date].replace(np.inf, 0).fillna(0).astype(int)
  if i < len(dates) - 1:
    pcol = dates[i + 1]
    percents.append(col + '%')
    df[col + '%'] = round((dft[date] / dft[dates[i + 1]].fillna(0) * 100) - 100).replace(np.inf, 0).fillna(0).astype(int).astype(str) + '%'


# %%
# df.set_index('Country', inplace=True)
df.style.set_table_styles(
    [{'selector': 'tr:hover',
      'props': [('background-color', 'black')]}]
).applymap(color_negative_red, subset=percents)
df

