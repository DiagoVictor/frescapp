import csv
import json
import zeep
import xmltodict
from datetime import datetime

def extractData(wsdl:str, serviceMethod:str, arg0:int)->object:
    client = zeep.Client(wsdl=wsdl)
    if serviceMethod == "promedioAbasSipsaMesMadr":
        return client.service.promedioAbasSipsaMesMadr()
    elif serviceMethod == "promediosSipsaCiudad":
        return client.service.promediosSipsaCiudad()
    elif serviceMethod == "promediosSipsaMesMadr":
        return client.service.promediosSipsaMesMadr()
    elif serviceMethod == "promediosSipsaParcial":
        return client.service.promediosSipsaParcial()
    elif serviceMethod == "promediosSipsaSemanaMadr":
        return client.service.promediosSipsaSemanaMadr()
    elif serviceMethod == "consultarInsumosSipsaMesMadr":
        return client.service.consultarInsumosSipsaMesMadr(arg0=arg0)

def transformData(getService:object, fields:list, date_filter:str)->object:
    response = []
    for record in getService:
        # Filtrar directamente con los atributos del objeto
        if hasattr(record, "deptNombre") and record.deptNombre == "BOGOTÁ, D.C." and record.enmaFecha.startswith(date_filter):
            data = {field: str(getattr(record, field, '')) for field in fields}
            response.append(data)
    return response


def loadData(pathFile:str, fields:list, data:object)->str:
    if pathFile.endswith('.json'):
        jsonData(pathFile, data)
    elif pathFile.endswith('.csv'):
        csvData(pathFile, fields, data)
    elif pathFile.endswith('.xml'):
        xmlData(pathFile, data)

def jsonData(pathFile:str, data:object)->None:
    with open(pathFile, "w", encoding="utf-8") as fData:
        json.dump(data, fData, ensure_ascii=False, indent=4)

def csvData(pathFile:str, fields:list, data:object)->None:
    with open(pathFile, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fields)
        for record in data:
            writer.writerow([record[field] for field in fields])

def xmlData(pathFile:str, data:object)->None:
    content = ""
    for i, elem in enumerate(data):
        mydict = {'return': elem}
        txt = xmltodict.unparse(mydict, pretty=True)
        if i > 0:
            txt = txt.replace("<?xml version=\"1.0\" encoding=\"utf-8\"?>", "")
        content += txt
    with open(pathFile, "w", encoding="utf-8") as fData:
        fData.write(content)

def controller(wsdl:str, serviceMethod:str, arg0:int, fields:list, pathFile:str, date_filter:str)->None:
    getService = extractData(wsdl, serviceMethod, arg0)
    print(">>> Data consultada.")
    data = transformData(getService, fields, date_filter)
    print(">>> Data transformada en objetos.")
    loadData(pathFile, fields, data)
    print(f">>> Data almacenada en archivo {pathFile[-4:]} en:", pathFile)

wsdl = 'https://appweb.dane.gov.co/sipsaWS/SrvSipsaUpraBeanService?WSDL'
serviceMethod = "promediosSipsaParcial"
arg0 = None
fields = [
    'artiNombre',
    'deptNombre',
    'enmaFecha',
    'fuenId',
    'fuenNombre',
    'futiId',
    'grupNombre',
    'idArtiSemana',
    'maximoKg',
    'minimoKg',
    'muniId',
    'muniNombre',
    'promedioKg'
]
date_filter = "2024-10-31"  # Fecha que deseas analizar
pathFile = "promediosSipsaParcial.json"

controller(wsdl, serviceMethod, arg0, fields, pathFile, date_filter)
