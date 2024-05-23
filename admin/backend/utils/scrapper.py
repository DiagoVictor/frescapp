import fitz  # PyMuPDF
import pandas as pd
import re

def extract_text_from_first_page(pdf_path):
    # Abre el archivo PDF
    document = fitz.open(pdf_path)
    page = document[0]  # Obtiene la primera página
    text = page.get_text("text")  # Extrae el texto de la primera página
    return text

def parse_table(text):
    # Divide el texto en líneas
    lines = text.split('\n')
    table_data = []
    
    # Supone que la primera línea contiene los encabezados de la tabla
    headers = [header.strip() for header in lines[0].split()]
    
    # Procesa las líneas siguientes para extraer las filas de la tabla
    for line in lines[1:]:
        # Utiliza una expresión regular para dividir las líneas en columnas
        columns = re.split(r'\s{2,}', line.strip())
        if len(columns) == len(headers):
            table_data.append(columns)
    
    # Crea un DataFrame de pandas a partir de los datos de la tabla
    df = pd.DataFrame(table_data, columns=headers)
    return df

def save_to_json(df, json_path):
    df.to_json(json_path, orient='records', lines=True)

def save_to_csv(df, csv_path):
    df.to_csv(csv_path, index=False)

# Ruta del archivo PDF
pdf_path = 'C:\Users\USUARIO\Documents\frescapp\admin\backend\utils\aaa.pdf'
# Extrae el texto de la primera página
text = extract_text_from_first_page(pdf_path)
# Parsea el texto para extraer la tabla
df = parse_table(text)
# Guarda la tabla en archivos JSON y CSV
save_to_json(df, 'tabla.json')
save_to_csv(df, 'tabla.csv')
