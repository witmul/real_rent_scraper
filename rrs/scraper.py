import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
from tqdm import tqdm
import sys

def initial_url(city):
    url = "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/" + city + "/"
    return url

def last_page(city):
    """
    This function picks number of last page of the
    initial link
    """

    print("Looking for last page")

    response_initial = requests.get(initial_url(city))
    soup = BeautifulSoup(response_initial.text, 'html.parser')
    pages = soup.findAll('div', attrs={"class": "css-4mw0p4"})
    last_page = int(pages[-1].text.split("...", 1)[1])
    return last_page

def load_flats_initial(city):
    """
    Function creates a table of flats containing:
    -Name
    -Price
    -Link
    -website
    """

    print("Loading initial table")

    page = 0

    df_new = pd.DataFrame()

    for x in range(page, last_page(city)):

        response = requests.get(initial_url(city) + "?page=" + str(x))
        soup = BeautifulSoup(response.text, 'html.parser')


        links = soup.findAll('a', attrs={"class": "css-1bbgabe"})
        titles = soup.findAll('h6', attrs={"class": "css-v3vynn-Text eu5v0x0"})
        prices = soup.findAll('p', attrs={"class": "css-l0108r-Text eu5v0x0"})

        #using re.compile to find a class that contains "marginright5 link linkWithHash" togather with Promoted flats
        # links = soup.findAll('a', attrs={"class": re.compile('.*marginright5 link linkWithHash.*')})
        # titles = soup.findAll('a', attrs={"class": re.compile('.*marginright5 link linkWithHash.*')})
        # prices = soup.findAll('p', attrs={"class": "price"})

        results_links = []
        results_names = []
        results_prices = []

        for l in links:
            l = l.get('href')
            results_links.append(l)

        for t in titles:
            #results_names.append(t.find("strong").text)
            results_names.append(t.text)

        for p in prices:
            #results_prices.append(p.find("strong").text)
            results_prices.append(p.text)

        df = pd.DataFrame({'Names': results_names,
                           'Price': results_prices,
                           'Links': results_links})

        df.replace(r'\s+|\\n', ' ', regex=True, inplace=True)
        df_new = df_new.append(df)

        results_site = []

        for site in df_new["Links"]:
            #after changes OLX site is not populating it's domain in links
            if site[1] == "d":
                df_new["Links"][df_new["Links"] == site] = "https://www.olx.pl" + site
                results_site.append("www.olx.pl")
            else:
                results_site.append(site.split("/")[2])

        df_new["Site"] = results_site

    return df_new

def olx_site(link):
    pattern_czynsz = re.compile('Czynsz')
    pattern_numb_rooms = re.compile('Liczba pokoi:')
    pattern_sqr = re.compile('Powierzchnia:')

    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')

    czynsz_i = soup.findAll('p', text=pattern_czynsz, attrs={"class": "css-xl6fe0-Text eu5v0x0"})
    try:
        czynsz = czynsz_i[0].text
        czynsz = czynsz.split(":")[-1].replace("zł", "")
    except:
        czynsz = 0

    numb_rooms_i = soup.findAll('p', text=pattern_numb_rooms, attrs={"class": "css-xl6fe0-Text eu5v0x0"})
    try:
        numb_rooms = numb_rooms_i[0].text
        numb_rooms = numb_rooms.split(" ")[-2]
    except:
        numb_rooms = 0


    sqr_i = soup.findAll('p', text=pattern_sqr, attrs={"class": "css-xl6fe0-Text eu5v0x0"})
    try:
        sqr = sqr_i[0].text
        sqr = sqr.split(" ")[-2]
    except:
        sqr = 0

    return czynsz, numb_rooms, sqr

def otodom_site(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')

    czynsz_i = soup.find('div', attrs={"aria-label": "Czynsz"})
    try:
        czynsz = czynsz_i.text
        czynsz = czynsz.replace(" ", "")
        czynsz = re.findall("\d+", czynsz)[0]
    except:
        czynsz = 0

    numb_rooms_i = soup.find('div', attrs={"aria-label": "Liczba pokoi"})
    try:
        numb_rooms = numb_rooms_i.text
        numb_rooms = re.findall("\d+", numb_rooms)[0]
    except:
        numb_rooms = 0

    sqr_i = soup.find('div', attrs={"aria-label": "Powierzchnia"})
    try:
        sqr = sqr_i.text
        sqr = re.findall("\d+", sqr)[0]
    except:
        sqr = 0

    return czynsz, numb_rooms, sqr

def load_flats_table(city):
    """
    This function will return a table with additional costs column and column with
    total of price + additional cost
    """

    df = load_flats_initial(city)
    czynsz_list, rooms_list, m2_list = [], [], []

    with tqdm(total=len(df), file=sys.stdout, desc="Progress") as pbar:
        for l, t in zip(df["Site"], df["Links"]):
            try:
                if l == "www.olx.pl":
                    results = [olx_site(t)]
                    czynsz_list.append(results[0][0])
                    rooms_list.append(results[0][1])
                    m2_list.append(results[0][2])
                elif l == "www.otodom.pl":
                    results = [otodom_site(t)]
                    czynsz_list.append(results[0][0])
                    rooms_list.append(results[0][1])
                    m2_list.append(results[0][2])
            except:
                czynsz_list.append("no details")
            pbar.update(1)

    try:
        df["Add_cost"] = czynsz_list

        df["Num of rooms"] = rooms_list
        df["Num of rooms"] = df["Num of rooms"].replace("pokoi:", "1")
        df["Num of rooms"] = df["Num of rooms"].replace("i", "4+")

        df["Size"] = m2_list
        df["Size"] = df["Size"].replace(np.nan, 0)

        df["Add_cost"] = df["Add_cost"].str.replace(" ", "")
        df["Add_cost"] = df["Add_cost"].str.replace(",", ".")
        df["Add_cost"] = df["Add_cost"].replace(np.nan, 0)

        df["Price"] = df["Price"].str.replace("zł", "")
        df["Price"] = df["Price"].str.replace(",", ".")
        df["Price"] = df["Price"].str.replace(" ", "")
        df["Price"] = df["Price"].str.replace("donegocjacji", "") #new update

        df["Size"] = df["Size"].str.replace(" ", "")
        df["Size"] = df["Size"].str.replace(",", ".")

        df["Total"] = df["Price"].astype(float) + df["Add_cost"].astype(float)
        df["zl/m2"] = df["Total"].astype(float) / df["Size"].astype(float)

        df["data"] = pd.to_datetime("today")
        df["miasto"] = city
    except:
        pass

    return df



