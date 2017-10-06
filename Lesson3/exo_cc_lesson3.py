import requests
import re
from token_olivier import API_KEY
from bs4 import BeautifulSoup
import pandas as pd
from multiprocessing import Pool
import time
import itertools


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


def get_top_towns(num=10):
    url = "https://lespoir.jimdo.com/2015/03/05/classement-des-plus-grandes-villes-de-france-source-insee/"

    soup = getSoupFromURL(url, 'get')

    if soup:
        print()
        cells = soup.find_all("td", class_='xl65', text=re.compile("\d{1,3}"))

        return [cell.findNext('td').text.strip() for cell in cells[:num] ]
    else :
        return []


def get_dist_matrix(origin, dest):

    r = requests.get(
    "https://maps.googleapis.com/maps/api/distancematrix/json?units=meters&origins={}, France&destinations={}, France&key={}".format(origin, dest, API_KEY)
    )

    assert r.status_code == 200

    return (r.json()['destination_addresses'][0].split(',')[0],
            r.json()['origin_addresses'][0].split(',')[0],
            r.json()['rows'][0]['elements'][0]['distance']['value'])


def parrallel_attempt(num=10):
    top_towns = get_top_towns(num)
    with Pool() as p:
        start_time = time.time()
        res_list = list(p.starmap(get_dist_matrix, [(a, b) for a in top_towns for b in top_towns]))
        print("Time elapsed : {} s".format(time.time() - start_time))

        df = pd.DataFrame()
        for abs, ord, value in res_list:
            df.loc[abs, ord] = value

        return df


def serial_attempt(num=10):
    top_towns = get_top_towns(num)

    start_time = time.time()
    res_list = list(itertools.starmap(get_dist_matrix, [(a, b) for a in top_towns for b in top_towns]))
    print("Time elapsed : {} s".format(time.time() - start_time))

    df = pd.DataFrame()
    for abs, ord, value in res_list :
        df.loc[abs, ord] = value

    return df


def benchmark_serial_vs_parallel(num=10):
    results = {}
    print("\n")
    for jobname, fct in zip(["Serial", "Parallel"], [serial_attempt, parrallel_attempt]):
        print(jobname + " job")
        init_time = time.time()
        res = fct(num)
        end_time = time.time()
        print("Done in {} s".format(end_time - init_time))

        results[jobname] = res

    return results


if __name__ == '__main__':
    res = benchmark_serial_vs_parallel(10)

    # Saving results to csv
    res["Parallel"].to_csv('top_10_towns_results.csv')
