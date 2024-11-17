from flask import Blueprint, jsonify, request
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
import locale
from locale import setlocale, LC_ALL
from babel import numbers
import locale

ue_api = Blueprint('ue', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
orders_collection = db['orders']
purchases_collection = db['purchases']
routes_collection = db['routes']
costs_collection = db["costs"]
unit_economics_collection = db['unit_economics']
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

@ue_api.route('/ue/<string:tipo>', methods=['GET'])
def ue(tipo):
    ue_list = list(unit_economics_collection.find({'tipo': str(tipo).capitalize()}, {'_id': 0}))
    return jsonify(ue_list), 200

@ue_api.route('/updateUE', methods=['POST'])
def updateUE():
    data = request.json
    fecha_base_str = data.get("dateUpdate")
    
    # Convertir la fecha de string a datetime
    fecha_base = datetime.strptime(fecha_base_str, "%Y-%m-%d")  # Ajusta el formato según cómo se pase la fecha
    nombre_mes = fecha_base.strftime('%B').capitalize()
    costos = {c['typeCost']: c['amount'] for c in costs_collection.find({"typePeriod" : "Mensual", "period": nombre_mes})}
    wh_rent = costos.get("wh_rent", 0)
    cost_tech = costos.get("cost_tech", 0)
    sales_force = costos.get("sales_force", 0)
    cost_others = costos.get("cost_others", 0)
    cost_supply = costos.get("cost_supply", 0)
    perssonel = costos.get("perssonel", 0)
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

    # Calcular unit economics para el mes y la semana
    for periodo, fecha_inicio, fecha_fin in [
        ("Mensual", inicio_mes, fin_mes),
        ("Semanal", inicio_semana, fin_semana)
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
        if periodo == "Mensual":
            wh_rent_distribuido = wh_rent
            cost_tech_distribuido = cost_tech
            sales_force_distribuido = sales_force
            otros_costos_distribuido = cost_others
            cost_insumos_distribuido = cost_supply
            cost_personal_distribuido = perssonel
        else:
            wh_rent_distribuido = wh_rent / 4
            cost_tech_distribuido = cost_tech / 4
            sales_force_distribuido = sales_force / 4
            otros_costos_distribuido = cost_others / 4
            cost_insumos_distribuido = cost_supply / 4
            cost_personal_distribuido = perssonel / 4

        # Calcular el total de costos fijos
        opex = round(wh_rent_distribuido + cost_tech_distribuido +  otros_costos_distribuido + cost_insumos_distribuido +costo_logistico + cost_personal_distribuido, 2)

        # Calcular métricas adicionales
        margen_neto  = round(gmv - cogs, 2)  # Utilidad antes de restar costos fijos
        utilidad_bruta = round(margen_neto - costo_logistico - opex - sales_force_distribuido, 2)  # Utilidad final después de todos los costos

        aov = round(gmv / total_ordenes, 2) if total_ordenes > 0 else 0
        mua = len(clientes)
        alv = round(gmv / total_lineas, 2) if total_lineas > 0 else 0  # Valor promedio por línea de ítem

        # Eliminar registros anteriores que coincidan con el periodo y mes o semana antes de insertar
        unit_economics_collection.delete_many({
            "tipo": periodo,
            "periodo": nombre_mes if periodo == "Mensual" else f"Semanal {fecha_base.isocalendar()[1]}"
        })

        def formato_dinero(valor):
            if valor is not None:
                return numbers.format_currency(valor, 'COP', locale='es_CO')
            return valor        
        unit_economics_collection.insert_one({
            "year": year,
            "tipo": periodo,
            "periodo": nombre_mes if periodo == "Mensual" else f"Semana {fecha_base.isocalendar()[1]}",
            "GMV": formato_dinero(gmv),
            "COGS": formato_dinero(cogs),
            "Last Mile": formato_dinero(costo_logistico),
            "WH Rent": formato_dinero(round(wh_rent_distribuido, 2)),
            "Tech Cost": formato_dinero(round(cost_tech_distribuido, 2)),
            "Sales Force": formato_dinero(round(sales_force_distribuido, 2)),
            "Others Cost": formato_dinero(round(otros_costos_distribuido, 2)),
            "Supply Cost": formato_dinero(round(cost_insumos_distribuido, 2)),
            "Perssonel" : formato_dinero(round(cost_personal_distribuido, 2)),
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
