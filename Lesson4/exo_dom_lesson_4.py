import collections
import operator
import pprint
import os
import json
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import time, random


def getSoupFromURL(url, method='get', data={}):
    if method == 'get':
        res = requests.get(url)
    elif method == 'post':
        res = requests.post(url, data=data)
    else:
        return None

    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup
    else:
        return None


def get_list_ads(force_update=False):
    filename = "ads_list.json"
    if os.path.exists(filename) and not force_update:
        with open(filename, 'r') as myfile:
            ads = json.load(myfile)
    else:
        url_search_pages = "https://www.leboncoin.fr/voitures/offres/{}/?o={}&q=renault%20zo%E9&f={}"
        url_search_ini = url_search_pages.replace("o={}&", "")
        curr_ad = 0
        ads = {}
        for region in ["ile_de_france", "aquitaine", "provence_alpes_cote_d_azur"]:
            ads[region] = {}
            for lpers, pers in zip(["p", "c"], ["particulier", "professionnel"]):
                ads[region][pers] = {}

                new_url = url_search_ini.format(region, lpers)
                soup = getSoupFromURL(new_url)

                # Result from first page

                ads_cells = soup.find_all("a", class_="list_item clearfix trackable")
                for cell in ads_cells:
                    curr_ad += 1
                    ads[region][pers][curr_ad] = {'title': cell['title'].strip(), 'link': 'https:' + cell["href"]}

                # If more results :

                cells_other_pages = soup.find_all("a", class_="element page", text=re.compile("\d{1,3}"), href=True)
                other_results_pages = {cell.text: 'https:' + cell["href"] for cell in cells_other_pages}
                if other_results_pages:
                    for num_page in other_results_pages:
                        page_url = other_results_pages[num_page]

                        # Result page
                        ads_cells = getSoupFromURL(page_url).find_all("a", class_="list_item clearfix trackable")
                        for cell in ads_cells:
                            curr_ad += 1
                            ads[region][pers][curr_ad] = {'title': cell['title'].strip(),
                                                          'link' : 'https:' + cell["href"]}
        with open(filename, 'w') as myfile:
            json.dump(ads, myfile)
    return ads


def get_car_infos(link):
    soup = getSoupFromURL(link)

    properties = list(map(lambda x: x.text.strip().lower(), soup.find_all("span", class_="property")))
    values = list(map(lambda x: x.text.strip().lower(), soup.find_all("span", class_="value")))

    attribs = {p: v for p, v in zip(properties, values)}

    description = soup.find_all("p", class_="value", itemprop="description")[0].text
    found_zoe = re.findall(r"zen|life|intens", description, flags=re.IGNORECASE | re.MULTILINE)
    found_tel = re.findall(r"(^(0|\+33)[1-9]([-. ]?[0-9]{2}){4}$)", description, flags=re.IGNORECASE | re.MULTILINE)

    if len(found_zoe) == 1:
        attribs["version"] = found_zoe[0].lower()
    elif len(found_zoe) == 0:
        attribs["version"] = ""
    else:
        found_zoe_str = " ".join(found_zoe).lower()
        counts = {pat: found_zoe_str.count(pat) for pat in "zen|life|intens".split("|")}
        attribs["version"] = max(counts.items(), key=operator.itemgetter(1))[0]

    if len(found_tel) == 0:
        attribs["telephone"] = ""
    else:
        attribs["telephone"] = found_tel[0].lower().replace(" ", "")

    # Cleaning

    attribs["prix"] = int(re.sub("\W", "", attribs["prix"]))
    attribs["kilométrage"] = int(re.sub("\D", "", attribs["kilométrage"]))
    attribs["année"] = int(re.sub("\D", "", attribs["année-modèle"]))

    for t in ["ville", "marque", 'boîte de vitesse', 'carburant', 'année-modèle']:
        del attribs[t]

    return attribs


def get_all_cars_infos(force_update=False):
    list_ads = get_list_ads(force_update)
    # pprint.pprint(list_ads)
    prix_argus = get_argus(force_update)
    # pprint.pprint(prix_argus)
    cols = ["version", "année", "kilométrage", "prix", "telephone", "pro/part", "prix Argus", "> argus ?"]

    # Loading already known data
    filename = "cars_data.csv"
    if os.path.exists(filename) and not force_update:
        df = pd.read_csv(filename, index_col=0)
    else:
        df = pd.DataFrame(columns=cols)

    # Setting dtypes
    for c in ["année", "kilométrage", "prix"]:
        df[c] = df[c].astype('int64')
    df["> argus ?"] = df["> argus ?"].astype('bool')
    nb_written = 0
    for region in list_ads:
        for pers in list_ads[region]:
            for num in list_ads[region][pers]:

                if nb_written > 3:
                    df.to_csv(filename)

                    return df, nb_written

                link = list_ads[region][pers][num]['link']
                title = list_ads[region][pers][num]['title']

                pdIndex = str(num) + " " + title

                if pdIndex in df.index:
                    continue
                else:
                    attribs = get_car_infos(link)
                    if not 'zo' in attribs['modèle'].lower():
                        continue
                    attribs["pro/part"] = pers
                    year_to_use = attribs['année']
                    if year_to_use < 2012:
                        year_to_use = 2012
                    version_to_use = attribs["version"]
                    if version_to_use == "":
                        version_to_use = 'zen'
                    pprint.pprint(attribs)
                    attribs["prix Argus"] = prix_argus[str(year_to_use)][str(version_to_use)]
                    attribs["> argus ?"] = attribs["prix"] > attribs["prix Argus"]

                    toAdd = collections.OrderedDict()
                    for c in cols:
                        toAdd[c] = attribs[c]

                    pprint.pprint(toAdd)

                    df.loc[pdIndex] = toAdd
                    nb_written += 1

                    # Waiting since no API...
                    waiting_time = random.uniform(5., 15.)
                    print("Waiting " + str(waiting_time) + " s not to overload leboncoin.fr")
                    time.sleep(waiting_time)

    df.to_csv(filename)

    return df, nb_written


def get_argus(force_update=False):
    filename = "argus.json"
    if os.path.exists(filename) and not force_update:
        with open(filename, 'r') as myfile:
            prix = json.load(myfile)
    else:
        prix = {}
        for year in list(map(str, range(2012, 2018))):
            prix[year] = {}
            for version in "zen|life|intens".split("|"):
                prix[year][version] = 0
                for supp in ["", "+type+2"]:
                    url = "http://www.lacentrale.fr/cote-auto-renault-zoe-{}+charge+rapide{}-{}.html".format(
                            version,
                            supp, year)
                    soup = getSoupFromURL(url)
                    tmp_prix = soup.find_all("span", class_="jsRefinedQuot")[0].text.replace(" ", "")
                    prix[year][version] += int(tmp_prix)

                prix[year][version] /= 2.

        with open(filename, 'w') as myfile:
            json.dump(prix, myfile)
    return prix


if __name__ == '__main__':
    # list_ads = get_list_ads(
    #         force_update=True
    # )
    # argus = get_argus(
    #         # force_update=True
    # )
    #
    # pprint.pprint(
    #     list_ads
    #     argus
    # )


    # Gently load cars not to get kicked by leboncoin.fr
    df, nb = get_all_cars_infos()
    print(df)

    while (nb > 0):
        df, nb = get_all_cars_infos()
        print(df)

    print(df)
