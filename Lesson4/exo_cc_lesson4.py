import requests
import re
import pandas as pd


medicaments = pd.DataFrame(columns = [
        "labo",
        "equiv sub active",
        "année commercialisation",
        "mois commercialisation",
        "prix",
        "restriction age",
        "restriction poids"
    ]
)

def get_info(id):
    url = "https://www.open-medicaments.fr/api/v1/medicaments/{}".format(id)
    my_json = requests.get(url).json()

    (year, month) = re.findall(r"(\d{4})-(\d{2})", my_json['presentations'][0]['dateDeclarationCommercialisation'])[0]
    labo = " ".join(my_json['titulaires'])
    prix = my_json['presentations'][0]['prix']
    qte_list = re.findall(r"(\d+)", my_json['substancesActives'][0]['dosageSubstance'])[0]
    if qte_list :
        qte = qte_list[0]
    else :
        qte = None

    age_list = re.findall(r"(\d+)\s*[aA]ns?", my_json['indicationsTherapeutiques'])
    if age_list:
        age = age_list[0]
    else:
        age = None

    poids_list = re.findall(r"(\d+)\s*(kg|Kg|kilo|Kilo)", my_json['indicationsTherapeutiques'])
    if poids_list:
        poids = poids_list[0][0]
    else:
        poids = None


    for nom_col, var in zip(["labo", "prix", "equiv sub active", "restriction age", "restriction poids", "année commercialisation", "mois commercialisation"],
                            [labo, prix, qte, age, poids, year, month]):
        medicaments.loc[id, nom_col] = var


if __name__ == '__main__':

    my_json = requests.get('https://www.open-medicaments.fr/api/v1/medicaments?query=ibuprofene').json()

    for i, el in enumerate(my_json) :
        medicaments.loc[el["codeCIS"], "denomination"] = el["denomination"]
        get_info(el["codeCIS"])

    print(medicaments)