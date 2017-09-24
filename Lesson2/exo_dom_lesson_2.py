import requests
import re
import pprint
from bs4 import BeautifulSoup


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

def get_values_for_A_to_E_using_regexp(year) :
    data = {'ICOM': '056', 'DEP': '075', 'TYPE': 'BPS', 'PARAM': 0, 'COMM': 0, 'EXERCICE': year}
    url = "http://alize2.finances.gouv.fr/communes/eneuro/tableau.php"

    htmlText = requests.post(url, data).text

    re_pattern = r"""<td class="libellepetit">[\w\sé'=]+=\s([A-E])</td>\s+<td class="montantpetit">(-?\d+\s*)+&nbsp;</td>\s+<td class="montantpetit">((-?\d+\s*)+)&nbsp;</td>"""
    found = re.findall(re_pattern, htmlText, flags=re.M)

    return { letter : int(value.replace(" ","")) for letter, _, value, _ in found }

def get_values_for_A_to_E_using_index_in_soup_class(year):
    index_of_interest = {
        'A': 1,
        'B': 4,
        'C': 10,
        'D': 13,
        'E': 16
    }
    data = {'ICOM': '056', 'DEP': '075', 'TYPE': 'BPS', 'PARAM': 0, 'COMM': 0, 'EXERCICE': year}
    url = "http://alize2.finances.gouv.fr/communes/eneuro/tableau.php"
    soup = getSoupFromURL(url, 'post', data)

    if soup:
        content = soup.find_all(class_="montantpetit")
        return { letter : int(content[index_of_interest[letter]].text.strip().replace(" ","")) for letter, i in index_of_interest.items() }

    else:
        return {}

def get_values_for_A_to_E_using_table_in_soup(year):
    data = {'ICOM': '056', 'DEP': '075', 'TYPE': 'BPS', 'PARAM': 0, 'COMM': 0, 'EXERCICE': year}
    url = "http://alize2.finances.gouv.fr/communes/eneuro/tableau.php"

    soup = getSoupFromURL(url, 'post', data)

    if soup:
        cells = soup.find_all("td", text=re.compile("=\s+([A-E])$"))
        labels = re.findall(r"=\s+([A-E])$", soup.prettify(), flags=re.M)
        # Values per inhabitant are 6 cells away from the one with the title
        cells_with_values_per_inhabitant = [cell.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling for cell in cells ]

        return {letter: int(cell.get_text().replace(" ", "")) for letter, cell in zip(labels, cells_with_values_per_inhabitant)}
    else:
        return {}

if __name__ == '__main__':

    liste_txt = [
        "Solution 1 : scrapping html pages with regexp",
        "Solution 2 : scrapping html pages with BeautifulSoup using class and known index",
        "Solution 3 : scrapping from a different url using html table structure"
    ]
    liste_fct = [
        get_values_for_A_to_E_using_regexp,
        get_values_for_A_to_E_using_index_in_soup_class,
        get_values_for_A_to_E_using_table_in_soup
    ]
    for solution, solver in zip(liste_txt, liste_fct) :
        print(solution + "\n")
        values = {i : solver(i) for i in range(2000, 2016)}
        pprint.pprint(values)
        print("\n")
