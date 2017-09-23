#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
url= "http://www.purepeople.com/article/laeticia-et-johnny-hallyday-leur-fille-jade-franchit-un-cap-avec-le-sourire_a252004/1"

def getNbViews(url = url, classename="c-sharebox__stats-number count") :
    res_req = requests.get(url)
    soup = BeautifulSoup(res_req.text, 'html.parser')

    out = soup.find_all(class_=classename )

    return int(out[0].text.strip())


if __name__ == '__main__':

        nb = getNbViews(url=url, classename="c-sharebox__stats-number count")
        print( nb )
