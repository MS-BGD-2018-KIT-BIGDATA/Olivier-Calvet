import requests
import re
import pprint
from bs4 import BeautifulSoup


def getValuesForAtoE(url) :
    htmlText = requests.get(url).text

    re_pattern = r"""<td class="montantpetit G">((-?\d+\s*)+)&nbsp;</td>\s+<td class="libellepetit G">[\w\sé'=]+=\s([A-E])</td>"""
    found = re.findall(re_pattern, htmlText, flags=re.M)

    return { letter : int(value.replace(" ","")) for value, _, letter in found }

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


def getValuesForPage(url, classname = "montantpetit G"):
    index_of_interest = {
        'A': 1,
        'B': 4,
        'C': 10,
        'D': 13,
        'E': 19
    }
    soup = getSoupFromURL(url)
    if soup:

        content = soup.find_all(class_=classname)
        return { letter : int(content[index_of_interest[letter]].text.strip().replace(" ","")) for letter, i in index_of_interest.items() }

    else:
        return {}


if __name__ == '__main__':

    print("Solution 1 : scrapping html pages with regexp")
    values = {}
    for i in range(2010, 2016):
        url = "http://alize2.finances.gouv.fr/communes/eneuro/detail.php?icom=056&dep=075&type=BPS&param=5&exercice={}".format(i)

        values[i] = getValuesForAtoE(url)

    pprint.pprint(values)


    print("Solution 2 : scrapping html pages with BeautifulSoup")
    values = {}
    for i in range(2010, 2016):
        url = "http://alize2.finances.gouv.fr/communes/eneuro/detail.php?icom=056&dep=075&type=BPS&param=5&exercice={}".format(i)

        values[i] = getValuesForPage(url)

    pprint.pprint(values)
