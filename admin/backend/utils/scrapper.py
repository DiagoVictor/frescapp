from dataclasses import replace
import json
import re
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    # Abre el archivo PDF
    document = fitz.open(pdf_path)
    pdf_text = []
    for page_num in range(len(document)):
        page = document[page_num]
        text = page.get_text("text")
        pdf_text.append(text)
        #print(f"Page {page_num + 1}:\n{text}\n{'-'*40}\n")
    return pdf_text

# Ruta del archivo PDF
pdf_path = f'C:/Users/USUARIO/Documents/frescapp/admin/backend/utils/aaa.pdf'

# Extrae el texto de todas las páginas y lo imprime
pdf_text = extract_text_from_pdf(pdf_path)

#print(pdf_text)

def procesar_texto(texto):
    if isinstance(texto, list):
        texto = ' '.join(map(str, texto))  # Join list elements into a string, ensure all elements are strings
    if not isinstance(texto, str):
        raise ValueError("Expected a string or a list of strings, got: {}".format(type(texto)))
    texto = texto.strip()
    secciones = re.split(r'[\n\r]+', texto)
    with open('raw_data.txt', 'w', encoding='utf-8') as file:
        file.write(str(texto))
    return secciones
def leer_y_convertir_a_json(ruta_archivo):
    productos = []

    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        # Leer todas las líneas del archivo
        lineas = archivo.readlines()
        
        # Descartar las primeras 7 líneas
        lineas = lineas[10:]
        del lineas[71]      #1
        del lineas[217:226] #9
        del lineas[231:244] #13
        lineas.insert(386,'CAJA')
        #del lineas[411]     #1
        del lineas[527:536] #9
        lineas.insert(450,'18')
        lineas.insert(457,'18')
        lineas.insert(464,'18')
        lineas.insert(471,'10')
        lineas.insert(492,'32')
        del lineas[616:623] #9
        del lineas[637:645] #9
        del lineas[785] 
        del lineas[840:] #9

        while lineas:
            bloque = lineas[:7]
            lineas = lineas[7:]  # Actualizar las líneas restantes
            # Crear un diccionario con la información del bloque
            try:
                producto = {
                    'name': bloque[0].strip(),
                    'presentation': bloque[1].strip(),
                    'quantity': bloque[2].strip(),
                    'unit': bloque[3].strip(),
                    'price_extra': bloque[4].replace('$', '').replace('.', '').strip(),
                    'price_primera': bloque[5].replace('$', '').replace('.', '').strip(),
                    'price_kg': bloque[6].replace('$', '').replace('.', '').strip()
                }
                
                # Añadir el producto a la lista de productos
                productos.append(producto)
            except Exception as e:
                print("Error "+ str(e))
        
    # Convertir la lista de productos a JSON
    json_output = json.dumps(productos, indent=4, ensure_ascii=False)
    
    # Guardar el JSON en un archivo
    with open('productos_output.json', 'w', encoding='utf-8') as json_file:
        json_file.write(json_output)
    
    return json_output

productos = procesar_texto(pdf_text)
ruta_archivo_txt = 'raw_data.txt'  # Cambia esto por la ruta real de tu archivo txt
json_resultado = leer_y_convertir_a_json(ruta_archivo_txt)
