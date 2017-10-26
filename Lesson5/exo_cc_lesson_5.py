import requests
import re
import pandas as pd


if __name__ == '__main__':
    filepath = "rpps-medecins-tab7_46218047883160.csv"
    df = pd.read_csv(filepath, encoding='latin-1', sep=";",  skiprows=[0,1,2,3,5])
    df = df.rename(columns={"SPECIALITE" : "Region"})
    df = df.set_index("Region")
    print(df.head())

#    nb_specialistes = df.copy()
    print(df[df["Chirurgie générale"] > 1.])

