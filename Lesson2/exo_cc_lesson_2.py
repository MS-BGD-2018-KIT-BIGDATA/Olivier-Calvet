import requests
import re
import pprint
from bs4 import BeautifulSoup

import numpy as np

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

def compare_pc_price(list_of_brands = ["acer", "dell"]) :
    if len(list_of_brands != 2) :
        print("Must provide a list of exactly 2 brands")
        return {}

    mean_discount = {}
    discounts = {}
    for model in list_of_brands :
        discounts[model] = []
        url = "https://www.cdiscount.com/search/10/{}+pc+portable.html".format(model)

        soup = getSoupFromURL(url, method='get')

        parent_cells = soup.find_all("div", class_="prdtBZPrice")

        for p in parent_cells :
            new_price = float([c.text for c in p.find_all("div", class_="prdtPrice")][0].replace("€","."))

            prev_prices_cells = [c.text for c in p.find_all("div", class_="prdtPrSt")]

            if prev_prices_cells:
                prev_price = float(prev_prices_cells[0].replace(",","."))
                discount = (1 - new_price / prev_price) * 100
            else :
                discount = 0

            discounts[model].append(discount)


        mean_discount[model] = np.mean(discounts[model])
    return mean_discount

if __name__ == '__main__':
    mean_discount = compare_pc_price()
    sorted_disc = sorted(mean_discount.items(), key= lambda x : x[1], reverse=True)

    # pprint.pprint(sorted_disc)
    #
    print("'{}' has more discount ({:.2f}% in avg) on pc than '{}' ({:.2f}% in avg) in the first page of results in cdiscount".format(sorted_disc[0][0],
                                                                                                     sorted_disc[0][1],
                                                                                                     sorted_disc[1][0],
                                                                                                     sorted_disc[1][1]))