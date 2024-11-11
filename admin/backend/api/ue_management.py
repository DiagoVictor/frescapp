from flask import Blueprint, jsonify, request
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
import locale
from locale import setlocale, LC_ALL
from babel import numbers
# Configurar la localización para obtener el nombre del mes en español
ue_api = Blueprint('ue', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
orders_collection = db['orders']
purchases_collection = db['purchases']
routes_collection = db['routes']
unit_economics_collection = db['unit_economics']


@ue_api.route('/ue/<string:tipo>', methods=['GET'])
def ue(tipo):
    ue_list = list(unit_economics_collection.find({'tipo': tipo}, {'_id': 0}))
    return jsonify(ue_list), 200

@ue_api.route('/updateUE', methods=['POST'])
def updateUE():
    data = request.json
    fecha_base_str = data.get("dateUpdate")
    
    # Convertir la fecha de string a datetime
    fecha_base = datetime.strptime(fecha_base_str, "%Y-%m-%d")  # Ajusta el formato según cómo se pase la fecha
    
    wh_rent = data.get("wh_rent")
    cost_tech = data.get("cost_tech")
    sales_force = data.get("sales_force")
    otros_costos = data.get("otros_costos")
    cost_insumos = data.get("cost_insumos")
    year = fecha_base.year
    inicio_mes = fecha_base.replace(day=1)
    fin_mes = inicio_mes + timedelta(days=32)
    fin_mes = fin_mes.replace(day=1) - timedelta(days=1)
    inicio_semana = fecha_base - timedelta(days=fecha_base.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    inicio_mes = inicio_mes.strftime('%Y-%m-%d')
    fin_mes = fin_mes.strftime('%Y-%m-%d')
    inicio_semana = inicio_semana.strftime('%Y-%m-%d')
    fin_semana = fin_semana.strftime('%Y-%m-%d')

    # Nombre del mes en español
    nombre_mes = fecha_base.strftime('%B')

    # Calcular unit economics para el mes y la semana
    for periodo, fecha_inicio, fecha_fin in [
        ("mensual", inicio_mes, fin_mes),
        ("semanal", inicio_semana, fin_semana)
    ]:
        cogs = 0
        total_ordenes = 0
        total_lineas = 0
        gmv = 0
        clientes = set()
        costo_logistico = 0

        # Filtrar órdenes en el rango de fechas
        ordenes = orders_collection.find({"delivery_date": {"$gte": fecha_inicio, "$lte": fecha_fin}})
        for orden in ordenes:
            total_ordenes += 1
            clientes.add(orden['customer_email'])
            for producto in orden['products']:
                quantity = producto['quantity']
                total_lineas = total_lineas + 1
                gmv += producto['price_sale'] * quantity

        # Calcular COGS de compras en el rango de fechas
        compras = purchases_collection.find({"date": {"$gte": fecha_inicio, "$lte": fecha_fin}})
        for compra in compras:
            for producto in compra['products']:
                if producto.get('final_price_purchase') is not None and producto.get('total_quantity_ordered') is not None:
                    cogs += round(float(producto['final_price_purchase']) * float(producto['total_quantity_ordered']), 2)

        # Calcular costo logístico total en el rango de fechas
        rutas = routes_collection.find({"close_date": {"$gte": fecha_inicio, "$lte": fecha_fin}})
        for ruta in rutas:
            costo_logistico += ruta['cost']

        # Calcular costos fijos e insumos distribuidos según el periodo
        if periodo == "mensual":
            wh_rent_distribuido = wh_rent
            cost_tech_distribuido = cost_tech
            sales_force_distribuido = sales_force
            otros_costos_distribuido = otros_costos
            cost_insumos_distribuido = cost_insumos
        else:
            wh_rent_distribuido = wh_rent / 4
            cost_tech_distribuido = cost_tech / 4
            sales_force_distribuido = sales_force / 4
            otros_costos_distribuido = otros_costos / 4
            cost_insumos_distribuido = cost_insumos / 4

        # Calcular el total de costos fijos
        opex = round(wh_rent_distribuido + cost_tech_distribuido +  otros_costos_distribuido + cost_insumos_distribuido +costo_logistico, 2)

        # Calcular métricas adicionales
        margen_neto  = round(gmv - cogs, 2)  # Utilidad antes de restar costos fijos
        utilidad_bruta = round(margen_neto - costo_logistico - opex - sales_force_distribuido, 2)  # Utilidad final después de todos los costos

        aov = round(gmv / total_ordenes, 2) if total_ordenes > 0 else 0
        mua = len(clientes)
        alv = round(gmv / total_lineas, 2) if total_lineas > 0 else 0  # Valor promedio por línea de ítem

        # Eliminar registros anteriores que coincidan con el periodo y mes o semana antes de insertar
        unit_economics_collection.delete_many({
            "tipo": periodo,
            "periodo": nombre_mes if periodo == "mensual" else f"semana {fecha_base.isocalendar()[1]}"
        })

        def formato_dinero(valor):
            if valor is not None:
                return numbers.format_currency(valor, 'COP', locale='es_CO')
            return valor        
        unit_economics_collection.insert_one({
            "year": year,
            "tipo": periodo,
            "periodo": nombre_mes if periodo == "mensual" else f"semana {fecha_base.isocalendar()[1]}",
            "GMV": formato_dinero(gmv),
            "COGS": formato_dinero(cogs),
            "Last Mile": formato_dinero(costo_logistico),
            "WH Rent": formato_dinero(round(wh_rent_distribuido, 2)),
            "Tech Cost": formato_dinero(round(cost_tech_distribuido, 2)),
            "Sales Force": formato_dinero(round(sales_force_distribuido, 2)),
            "Others Cost": formato_dinero(round(otros_costos_distribuido, 2)),
            "Supply Cost": formato_dinero(round(cost_insumos_distribuido, 2)),
            "Opex": formato_dinero(opex),
            "Net Profit": formato_dinero(utilidad_bruta),
            "Gross Profit as % of GMV": formato_dinero(100-((cogs*100)/gmv)),
            "Gross Profit": formato_dinero(margen_neto),
            "Orders": total_ordenes,
            "Lines": total_lineas,
            "AOV": formato_dinero(aov),
            "ALV": formato_dinero(alv),
            "MUA": mua
        })

    return jsonify({"message": "Unidad económica actualizada exitosamente"}), 200
