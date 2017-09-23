import requests
from bs4 import BeautifulSoup


url = 'http://www.purepeople.com/article/caroline-de-maigret-ce-jour-ou-yarol-poupaud-a-quitte-sa-copine-pour-elle_a251827/1'
share_class_pp = "c-sharebox__stats-number"

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

def getNumberOfSharesForPage(url, classname):
  soup = getSoupFromURL(url)
  if soup:

    share_content = soup.find_all(class_=classname)[0].text.strip()
    if 'K' in share_content:
      #remove the K at the end with -1
      parts = share_content[:-1].split(',')
      return int(parts[0])*1000 + int(parts[1])*100
    else:
      return int(share_content)
  else:
    0

def getListOfArticlesForPeople(people):
  #url_search = "http://www.purepeople.com/rechercher/"
  #params = {"q": people}
  #results_search  = getSoupFromURL(url_search, 'post', params)

  url_search = "http://www.purepeople.com/rechercher/q/" + people + "/cat/article/np/"
  class_result = "c-article-flux__title"
  results_search = []
  for i in range(1,2):
    soup_results_search  = getSoupFromURL(url_search+str(i))
    results_search += [a['href'] for a in soup_results_search.find_all("a", class_=class_result)]
  return results_search


#all_pages_people_1 = getListOfArticlesForPeople('johnny')
all_pages_people_2 = getListOfArticlesForPeople('angelina')

#shares_people_1 = []
shares_people_2 = []
for page in all_pages_people_2:
  print '-----'
  print page
  share = getNumberOfSharesForPage("http://www.purepeople.com" + page, share_class_pp)
  print share
  shares_people_2.append(share)
