import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
from tqdm import tqdm
import sys

from rrs.user_input import select_city


def initial_url(city):
    url = "https://www.olx.pl/d/nieruchomosci/mieszkania/wynajem/" + city + "/"
    return url


def last_page(city):
    """
    This function picks number of last page of the
    initial link
    """

    print("Looking for last page")

    response_initial = requests.get(initial_url(city))
    soup = BeautifulSoup(response_initial.text, 'html.parser')
    pages = soup.findAll('a', attrs={"class": "css-1mi714g"})
    last_page = int(pages[-1].text.split(None, 1)[0])
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

        # links = soup.findAll('a', href=re.compile("/d/oferta/"))
        links = soup.findAll('a', attrs={"class": "css-1bbgabe"})
        titles = soup.findAll('p', attrs={"class": "css-cqgwae-Text eu5v0x0"})
        prices = soup.findAll('p', attrs={"class": "css-1v0u9e8-Text eu5v0x0"})

        results_links = []
        results_names = []
        results_prices = []

        for l in links:
            l = l.get('href')
            if l.split("/")[2] != "www.otodom.pl":
                results_links.append("https://www.olx.pl" + l)
            else:
                results_links.append(l)
        for t in titles:
            results_names.append(t.text)
        for p in prices:
            results_prices.append(p.text)

        df = pd.DataFrame({'Names': results_names,
                           'Price': results_prices,
                           'Links': results_links})

        df.replace(r'\s+|\\n', ' ', regex=True, inplace=True)
        df_new = df_new.append(df)

        results_site = []

        for site in df_new["Links"]:
            results_site.append(site.split("/")[2])

        df_new["Site"] = results_site

    return df_new


def olx_site_cost(link):
    """
    Based on Site value from final table of function load_flats_initial() return
    this function will call a link from above table, and extract additional cost number from a page
    """

    pattern = re.compile('Czynsz')
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    additional_val = soup.findAll('p', text=pattern, attrs={"class": "css-xl6fe0-Text eu5v0x0"})
    # additional_val = soup.findAll('p', attrs={"class": "css-xl6fe0-Text eu5v0x0"})
    try:
        value = additional_val[0].text

        value = value.split(":")[-1].replace("zł", "")
    except:
        value = 0
    return value


def olx_site_rooms(link):
    """
    Based on Site value from final table of function load_flats_initial() return
    this function will call a link from above table, and extract number of rooms from a page
    """

    pattern = re.compile('Liczba pokoi:')
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    additional_val = soup.findAll('p', text=pattern, attrs={"class": "css-xl6fe0-Text eu5v0x0"})
    # additional_val = soup.findAll('p', attrs={"class": "css-xl6fe0-Text eu5v0x0"})
    try:
        value = additional_val[0].text
        value = value.split(" ")[-2]
    except:
        value = 0
    return value


def olx_site_m2(link):
    """
    Based on Site value from final table of function load_flats_initial() return
    this function will call a link from above table, and extract size of rooms from a page
    """

    pattern = re.compile('Powierzchnia:')
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    additional_val = soup.findAll('p', text=pattern, attrs={"class": "css-xl6fe0-Text eu5v0x0"})
    # additional_val = soup.findAll('p', attrs={"class": "css-xl6fe0-Text eu5v0x0"})
    try:
        value = additional_val[0].text
        value = value.split(" ")[-2]
    except:
        value = 0
    return value


def otodom_site_cost(link):
    """
    Based on Site value from final table of function load_flats_initial() return
    this function will call a link from above table, and extract additional cost number from a page
    """

    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    additional_val = soup.find('div', attrs={"title": "Czynsz - dodatkowo"})
    try:
        value = additional_val.find_next_siblings()[1].text
        value = value.split(" ")[-2]
    except:
        value = 0
    return value


def otodom_site_rooms(link):
    """
    Based on Site value from final table of function load_flats_initial() return
    this function will call a link from above table, and extract number of rooms from a page
    """

    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    additional_val = soup.find('div', attrs={"title": "Liczba pokoi"})
    try:
        value = additional_val.find_next_siblings()[0].text
        # value = value.split(" ")[-2]
    except:
        value = 0
    return value


def otodom_site_m2(link):
    """
    Based on Site value from final table of function load_flats_initial() return
    this function will call a link from above table, and extract size of rooms from a page
    """

    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    additional_val = soup.find('div', attrs={"title": "Powierzchnia"})
    try:
        if len(additional_val.find_next_siblings()) > 1:  # stupid thing. it takes random html line from web
            value = additional_val.find_next_siblings()[1].text.split(" ")[0]
        else:
            value = additional_val.find_next_siblings()[0].text.split(" ")[0]
    except:
        value = 0
    return value


def load_flats_table(city):
    """
    This function will return a table with additional costs column and column with
    total of price + additional cost
    """

    df = load_flats_initial(city)
    czynsz_list = []
    rooms_list = []
    m2_list = []
    with tqdm(total=len(df), file=sys.stdout, desc="Progress") as pbar:
        for l, t in zip(df["Site"], df["Links"]):
            try:
                if l == "www.olx.pl":
                    czynsz_list.append(olx_site_cost(t))
                    rooms_list.append((olx_site_rooms(t)))
                    m2_list.append((olx_site_m2(t)))
                elif l == "www.otodom.pl":
                    czynsz_list.append(otodom_site_cost(t))
                    rooms_list.append(otodom_site_rooms(t))
                    m2_list.append(otodom_site_m2(t))
            except:

                czynsz_list.append("no details")
            pbar.update(1)

    try:
        df["Add_cost"] = czynsz_list
        df["Num of rooms"] = rooms_list
        df["Num of rooms"] = df["Num of rooms"].replace("pokoi:", "1")
        df["Num of rooms"] = df["Num of rooms"].replace("i", "4+")
        df["Size"] = m2_list

        df["Add_cost"] = df["Add_cost"].str.replace(" ", "")
        df["Add_cost"] = df["Add_cost"].str.replace(",", ".")
        df["Add_cost"] = df["Add_cost"].replace(np.nan, 0)

        df["Price"] = df["Price"].str.replace("zł", "")
        df["Price"] = df["Price"].str.replace(",", ".")
        df["Price"] = df["Price"].str.replace(" ", "")

        df["Size"] = df["Size"].str.replace(" ", "")
        df["Size"] = df["Size"].str.replace(",", ".")

        df["Total"] = df["Price"].astype(float) + df["Add_cost"].astype(float)
        df["zl/m2"] = df["Total"].astype(float) / df["Size"].astype(float)

        df["data"] = pd.to_datetime("today")
        df["miasto"] = city
    except:
        pass

    return df



