import requests
import re
import pprint
from bs4 import BeautifulSoup
import pandas as pd
from multiprocessing import Pool
import time


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


def get_top_contribs():
    url = "https://gist.github.com/paulmillr/2657075"

    soup = getSoupFromURL(url, 'get')

    if soup:
        cells = [cell.parent for cell in soup.find_all("th", text=re.compile("#\d{1,3}"))]

        return {cell.a.text: cell.a["href"] for cell in cells if cell.a and cell.a.text and cell.a["href"]}

    else:
        return {}


def get_user_repos_avg_stargazers(username):
    my_headers = {'Authorization': 'token 8d4b3d71a772bb928182cb04e3211e63936deb62'}
    r = requests.get("https://api.github.com/users/{}/repos".format(username)
                     , headers=my_headers
                     )
    assert r.status_code == 200

    # For debugging
    # return { repo['full_name'] : repo["stargazers_count"] for repo in r.json() }
    return pd.Series([repo["stargazers_count"] for repo in r.json()]).mean()


def parrallel_attempt():
    with Pool() as p:
        top_contribs = get_top_contribs()

        start_time = time.time()
        res_list = p.map(get_user_repos_avg_stargazers, top_contribs.keys())
        print("\nTime elapsed to get avg stargazer per user : {} s".format(time.time() - start_time))

        return pd.Series(index=top_contribs, data=res_list).sort_values(ascending=False)


def serial_attempt():
    top_contribs = get_top_contribs()
    assert len(top_contribs) == 256

    start_time = time.time()
    res_list = list(map(get_user_repos_avg_stargazers, top_contribs.keys()))
    print("\nTime elapsed to get avg stargazer per user : {} s".format(time.time() - start_time))

    return pd.Series(index=top_contribs, data=res_list).sort_values(ascending=False)


def benchmark_serial_vs_parallel():
    results = {}
    for jobname, fct in zip(["Serial", "Parallel"], [serial_attempt, parrallel_attempt]):
        print(jobname + " job")
        init_time = time.time()
        res = fct()
        end_time = time.time()
        print("\nDone in {} s".format(end_time - init_time))

        results[jobname] = res

        # print(results["Serial"] - results["Parallel"])


if __name__ == '__main__':
    # benchmark_serial_vs_parallel()

    res = parrallel_attempt()
    print("Top 256 contributors of 'https://gist.github.com/paulmillr/2657075'",
          " rank by the average stargazers of their repos : \n")
    print(res)
