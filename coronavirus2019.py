# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython


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
from sys import platform

repo = "https://github.com/CSSEGISandData/COVID-19"

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

def cdate(date):
  if platform == 'win32':
    return date.strftime("%#m/%#d/%y")
  else:
    return date.strftime("%-m/%-d/%y")

def datecols(df):
  return [col for i, col in enumerate(df.columns) if is_date(col) ]

def update_firsts(df, firsts_col):
  # Get date of first death or days since first death.
  df[f'{firsts_col}'] = ''
  dates = sorted([parser.parse(col) for col in df.columns if is_date(col) ])
  # print(f"{firsts_col} dates:", dates, df.columns)
  for i, row in df.iterrows():
    found_first = False
    for date in dates:
      try:
        if not found_first and row[cdate(date)] > 0:
          found_first = True
          df.at[i, firsts_col] = date.strftime('%Y-%m-%d')
          # print(f"update_firsts(df, {firsts_col}):\n", date, row[date])
      except Exception as e:
        # pass
        print(f"### ERROR update_firsts(df, {firsts_col}):\n", cdate(date), row, e)
  # print(f"update_firsts({firsts_col})\n", df.iloc[:3])

def is_date(text):
  try:
    s = parser.parse(text)
    return True
  except:
    return False

def hotten(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    heat = str(hex(min(int(val.replace('%', '')) * 10 + 56, 255))).split('x')[-1].upper()
    color = f'#{heat}5555'
    result = 'color: %s;' % color
    # print(val, result)
    return result


# %%
df = pd.read_csv(tsc_csv).drop(columns=['Lat', 'Long'])
dates = datecols(df)
today_col = dates[-1]
dates.reverse()

dfr = pd.read_csv(tsr_csv)
dfm = pd.read_csv(tsm_csv).drop(columns=['Lat', 'Long'])
df.rename(columns={'Country/Region': 'Country', 'Province/State': 'State'}, inplace=True)
dfm.rename(columns={'Country/Region': 'Country', 'Province/State': 'State'}, inplace=True)
df['Country'].replace('Mainland China', 'China', inplace=True)
df['Country'].replace('United Arab Emirates', 'UAE', inplace=True)
dfm['Country'].replace('Mainland China','China', inplace=True)
dfm['Country'].replace('United Arab Emirates', 'UAE', inplace=True)
mdates = datecols(dfm)

update_firsts(df, 'First Confirmed')
update_firsts(dfm, 'First Death')

dfm.set_index(['Country', 'State'], inplace=True)
df.fillna('')
df['Country'].fillna('')
dfm.fillna('')

df.set_index(['Country', 'State'], inplace=True)
df['Death Toll'] = dfm[today_col].fillna(0).apply(lambda toll: int(toll))
df['First Death'] = dfm[dfm.columns[-1]].fillna('')
df['Death Aging'] = datetime.now() - df['First Death'].apply(lambda date: parser.parse(date, fuzzy=True) if is_date(date) else '')
df['Death Aging'] = df['Death Aging'].apply(lambda days: ' '.join(str(days).replace('NaT', '').split(' ')[:2]))
df.drop(columns=['First Death'], inplace=True)

df['Confirmed Aging'] = datetime.now() - df['First Confirmed'].apply(lambda date: parser.parse(date, fuzzy=True))
df['Confirmed Aging'] = df['Confirmed Aging'].apply(lambda days: ' '.join(str(days).split(' ')[:2]))
df.drop(columns=['First Confirmed'], inplace=True)

percents = []
drop_dates = []
rev_dates = sorted([parser.parse(date) for date in dates], reverse=True)
for i, date in enumerate(rev_dates):
  date = cdate(date)
  d = parser.parse(date)
  col = d.strftime('%B')[:3] + d.strftime('%d')

  df[col] = df[date].replace(np.inf, 0).fillna(0).astype(int)
  if i < len(dates) - 1:
    pcol = dates[i + 1]
    pct_idx = df.columns.get_loc(pcol)
    pct_col = col + '%'
    percents.append(pct_col)
    pct_val = round((df[date] / df[dates[i + 1]].fillna(0) * 100) - 100).replace(np.inf, 0).fillna(0).astype(int).astype(str) + '%'
    drop_dates.append(date)
    # df.insert(pct_idx, pct_col, pct_val)
    df[pct_col] = pct_val
df.drop(columns=dates, inplace=True)


# %%
# df.set_index('Country', inplace=True)
sytled_df = df.style.set_table_styles(
    [{'selector': 'tr:hover',
      'props': [('background-color', 'black')]}]
).applymap(hotten, subset=percents)
file = open("docs/index.html", "w")
file.write(sytled_df.render())



# %%
