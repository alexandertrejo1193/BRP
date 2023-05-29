import requests
from bs4 import BeautifulSoup
from lxml import html
from lxml import etree
import pandas as pd
from geopy.geocoders import Nominatim
import numpy as np
url = "https://www.lamudi.com.mx/puebla/for-sale/"
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
}
response = requests.get(url, headers=headers)
soup=BeautifulSoup(response.text)
ultpagfrase= soup.find('div',attrs={"class":"pagination__pages"}).text
ultpagfrase=ultpagfrase.split("\n")
while "" in ultpagfrase:
    ultpagfrase.remove("")
ultpagfrase=ultpagfrase[0].split(" ")
while "" in ultpagfrase:
    ultpagfrase.remove("") 
ini=int(ultpagfrase[1])
can=int(ultpagfrase[3])
print(ini,can)
siguiente=url
listaurl=[]
while True:
    #empieza un ciclo para obtener todas las url de cada pagina que arrojo la busqueda
    r =requests.get(siguiente)
    if r.status_code==200:
        dom=etree.HTML(str(soup))
        url = siguiente
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        }
        response = requests.get(url, headers=headers)
        soup=BeautifulSoup(response.text)
        contendedor_url=soup.find('div',attrs={'class':'listings__cards notSponsored'})

        for i in contendedor_url.find_all('a'):
            listaurl.append("https://www.lamudi.com.mx"+i['href'])
        ini+=1
        print(ini,can) 
    else:
        print(ini) 
        break
    if ini==can:
        break
    siguiente=soup.find('a',attrs={'id':'pagination-next'}).get('href')
import re
print(len(listaurl))
longurls=len(listaurl)
listurl=[""]*longurls
lista_titulo=[""]*longurls
lista_precio=[""]*longurls
lista_ubi=[""]*longurls
lista_atributos=[""]*longurls
lista_tipo=[""]*longurls
lista_tipo_op=[""]*longurls
lista_carac=[""]*longurls
lista_num_carac=[""]*longurls

ind=0
for url in listaurl:
    listurl[ind]=url
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    }
    response = requests.get(url, headers=headers)
    soup=BeautifulSoup(response.text)
    lista_titulo[ind]=soup.find('div',attrs={'class':'main-title'}).text
    lista_precio[ind]=soup.find('div',attrs={'class':'prices-and-fees__price'}).text
    lista_ubi[ind]=soup.find('div',attrs={'class':'view-map__text'}).text
    try:
        lista_atributos[ind]=soup.find_all('div',attrs={'class':'details-item-value'})
    except:
        a=1
    try:
        lista_tipo[ind]=soup.find('div',attrs={'class':'property-type'}).find('span',attrs={'class':'place-features__values'}).text
    except:
        a=1
    try:
        lista_tipo_op[ind]=soup.find('div',attrs={'class':'operation-type'}).find('span',attrs={'class':'place-features__values'}).text
    except:
        a=1
    try:
        lista_carac[ind]=soup.find_all('div',attrs={'class':'facilities__item'})
    except:
        a=1
    try:
        lista_carac[ind] = [re.sub('<[^<]+?>', '', str(elemento)) for elemento in lista_carac[ind]]
    except:
        a=1
    try:
        lista_num_carac[ind]=len(lista_carac[ind])
    except:
        a=1
    
    ind+=1
    print(ind,len(listaurl))
df=pd.DataFrame({"Url":listurl ,"Titulo":lista_titulo ,"Ubicación":lista_ubi,"Precio":lista_precio,"lista_atributos":lista_atributos,
                "Tipo de inmueble":lista_tipo,"Tipo de operación":lista_tipo_op,"Características":lista_carac,"# Características":lista_num_carac})
def quitcomillas(celda):
    try:
        return celda.replace(",", "")
    except:
        return ""


def extraer_numero(celda):
    try:
        return int(re.findall(r'\d+', celda)[0])
    except:
        return 0

df['Precio']=df['Precio'].apply(quitcomillas).apply(extraer_numero)

df_1 = df
unique_values = set([value for sublist in df_1['Características'] for value in sublist])
for value in unique_values:
    df_1[value] = df_1['Características'].apply(lambda x: int(value in x))

def extraer_ubicacion(elemento):
    elemento1 = elemento.split(",")
    if len(elemento1)==3:
        estado=elemento1[2]
        municipio=elemento1[1]
        colonia=elemento1[0]
    elif len(elemento1)==2:
        estado=elemento1[1]
        municipio=elemento1[0]
        colonia=np.nan
    else:
        estado=elemento1[0]
        municipio=np.nan
        colonia=np.nan
        

    return pd.Series([estado, municipio, colonia])
df_1[['Estado', 'Municipio', 'Colonia']] = df_1['Ubicación'].apply(extraer_ubicacion)
geolocator = Nominatim(user_agent="my_geocoder")

def obtener_latitud_longitud(direccion):
    try:
        location = geolocator.geocode(direccion)
        if location is not None:
            return location.latitude, location.longitude
        else:
            return pd.NA, pd.NA
    except:
        return pd.NA, pd.NA
    
df_1['Direccion'] = df_1['Municipio'] + ', ' + df_1['Estado']
df_1['Latitud'], df_1['Longitud'] = zip(*df_1['Direccion'].apply(obtener_latitud_longitud))
df_1['Latitud1'], df_1['Longitud2'] = zip(*df_1['Colonia'].apply(obtener_latitud_longitud))
df_1.to_excel('Data.xlsx',index=False)
