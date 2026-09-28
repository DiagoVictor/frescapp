import { Component, OnInit } from '@angular/core';
import { OrderService } from '../../services/order.service';
import { PurchaseService } from '../../services/purchase.service';
import { CostsService } from '../../services/costs.service';
import { UnitEconomicsService } from '../../services/unit-economics.service';
import { forkJoin } from 'rxjs';
import * as XLSX from 'xlsx';
import * as FileSaver from 'file-saver';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.css']
})
export class ReportsComponent implements OnInit {
  selectedMonth: string = new Date().toISOString().slice(0, 7);
  downloading = false;
  errorMsg = '';

  constructor(
    private orderService: OrderService,
    private purchaseService: PurchaseService,
    private costsService: CostsService,
    private unitEconomicsService: UnitEconomicsService
  ) { }

  ngOnInit(): void { }

  downloadExcel() {
    if (!this.selectedMonth) return;
    this.downloading = true;
    this.errorMsg = '';

    const [year, month] = this.selectedMonth.split('-').map(Number);
    const startDate = `${this.selectedMonth}-01`;
    const lastDay = new Date(year, month, 0).getDate();
    const endDate = `${this.selectedMonth}-${lastDay.toString().padStart(2, '0')}`;

    forkJoin({
      orders: this.orderService.getOrders(startDate, endDate),
      purchases: this.purchaseService.getPurchases(),
      costs: this.costsService.getCostos(),
      ue: this.unitEconomicsService.getUnitEconomics()
    }).subscribe({
      next: ({ orders, purchases, costs, ue }) => {
        const filteredPurchases = (purchases || []).filter((p: any) =>
          p.date && p.date.startsWith(this.selectedMonth)
        );
        const filteredCosts = (costs || []).filter((c: any) => {
          if (!c.period) return false;
          // Convertimos a String por si viene como Date o número
          return String(c.period).startsWith(this.selectedMonth);
        });

        const workbook = XLSX.utils.book_new();

        // --- Hoja 1: Pedidos ---
        const pedidosData: any[] = [];
        (orders || []).forEach((order: any) => {
          const productos = order.products && order.products.length > 0 ? order.products : [null];
          productos.forEach((product: any) => {
            pedidosData.push({
              'Número Pedido': order.order_number,
              'Cliente': order.customer_name,
              'Email': order.customer_email,
              'Teléfono': order.customer_phone,
              'Fecha Entrega': order.delivery_date,
              'Estado': order.status,
              'Método Pago': order.paymentMethod,
              'Vendedor': order.seller_name,
              'Domiciliario': order.driver_name,
              'SKU': product?.sku || '',
              'Producto': product?.name || '',
              'Unidad': product?.unit || '',
              'Cantidad': product?.quantity || 0,
              'Precio Unitario': product?.price_sale || 0,
              'Total Producto': (product?.quantity || 0) * (product?.price_sale || 0),
              'Total Pedido': order.total || 0,
              'Descuento': order.discount || 0,
              'Costo Envío': order.deliveryCost || 0
            });
          });
        });
        XLSX.utils.book_append_sheet(workbook, XLSX.utils.json_to_sheet(pedidosData.length > 0 ? pedidosData : [{ 'Sin datos': '' }]), 'Pedidos');

        // --- Hoja 2: Compras ---
        const comprasData: any[] = [];
        filteredPurchases.forEach((purchase: any) => {
          const productos = purchase.products && purchase.products.length > 0 ? purchase.products : [null];
          productos.forEach((product: any) => {
            comprasData.push({
              'Número Compra': purchase.purchase_number,
              'Fecha': purchase.date,
              'Estado': purchase.status,
              'SKU': product?.sku || '',
              'Producto': product?.name || '',
              'Categoría': product?.category || '',
              'Cantidad': product?.total_quantity || product?.quantity || 0,
              'Precio Sugerido': product?.price_purchase || 0,
              'Precio Real': product?.final_price_purchase || 0,
              'Total Sugerido': (product?.price_purchase || 0) * (product?.total_quantity || product?.quantity || 0),
              'Total Real': (product?.final_price_purchase || 0) * (product?.total_quantity || product?.quantity || 0),
              'Estado Producto': product?.status || ''
            });
          });
        });
        XLSX.utils.book_append_sheet(workbook, XLSX.utils.json_to_sheet(comprasData.length > 0 ? comprasData : [{ 'Sin datos': '' }]), 'Compras');

        // --- Hoja 3: Costos ---
        const costosData = filteredCosts.map((c: any) => ({
          'Tipo Costo': c.typeCost,
          'Detalle': c.detail,
          'Monto': c.amount,
          'Tipo Período': c.typePeriod,
          'Período': c.period
        }));
        XLSX.utils.book_append_sheet(workbook, XLSX.utils.json_to_sheet(costosData.length > 0 ? costosData : [{ 'Sin datos': '' }]), 'Costos');

        // --- Hojas 4-6: UE Mensual / Semanal / Diario ---
        const groupedUE = this.groupUEByDate(ue || [], this.selectedMonth);

        const ueMensual = this.buildUESheet(groupedUE, 'mes');
        XLSX.utils.book_append_sheet(workbook, XLSX.utils.json_to_sheet(ueMensual.length > 0 ? ueMensual : [{ 'Sin datos': '' }]), 'UE Mensual');

        const ueSemanal = this.buildUESheet(groupedUE, 'semana');
        XLSX.utils.book_append_sheet(workbook, XLSX.utils.json_to_sheet(ueSemanal.length > 0 ? ueSemanal : [{ 'Sin datos': '' }]), 'UE Semanal');

        const ueDiario = this.buildUESheet(groupedUE, 'dia');
        XLSX.utils.book_append_sheet(workbook, XLSX.utils.json_to_sheet(ueDiario.length > 0 ? ueDiario : [{ 'Sin datos': '' }]), 'UE Diario');

        // --- Descargar ---
        const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
        const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        FileSaver.saveAs(blob, `Reporte_Frescapp_${this.selectedMonth}.xlsx`);
        this.downloading = false;
      },
      error: (err) => {
        console.error('Error descargando reporte:', err);
        this.errorMsg = 'Error al descargar el reporte. Intenta de nuevo.';
        this.downloading = false;
      }
    });
  }

  private groupUEByDate(data: any[], month: string): { [fecha: string]: any[] } {
    return data.reduce((acc: { [fecha: string]: any[] }, item: any) => {
      if (item.fecha && item.fecha.startsWith(month)) {
        if (!acc[item.fecha]) acc[item.fecha] = [];
        acc[item.fecha].push(item);
      }
      return acc;
    }, {});
  }

  private buildUESheet(groupedData: { [fecha: string]: any[] }, tipo: 'mes' | 'semana' | 'dia'): any[] {
    const fechas = Object.keys(groupedData).sort();
    if (fechas.length === 0) return [];

    let periodos: string[];
    if (tipo === 'mes') {
      periodos = [...new Set(fechas.map(f => f.slice(0, 7)))];
    } else if (tipo === 'semana') {
      periodos = [...new Set(fechas.map(f => this.getSemanaISO(f)))].sort();
    } else {
      periodos = fechas;
    }

    const variables = [
      { key: 'gmv', label: 'GMV' },
      { key: 'cogs', label: 'COGS' },
      { key: 'logistics_cost', label: 'Costo Logístico' },
      { key: 'perssonel', label: 'Costo de Personal' },
      { key: 'cost_tech', label: 'Costo de Tecnología' },
      { key: 'warehouse', label: 'Rentas de Almacén' },
      { key: 'cost_others', label: 'Otros Costos' },
      { key: 'total_orders', label: 'Órdenes' },
      { key: 'total_lines', label: 'Líneas' }
    ];

    const rows: any[] = [];

    variables.forEach(v => {
      const row: any = { 'Indicador': v.label };
      periodos.forEach(periodo => {
        row[periodo] = this.getUEValor(groupedData, fechas, periodo, tipo, v.key);
      });
      rows.push(row);
    });

    // AOV
    const aovRow: any = { 'Indicador': 'AOV' };
    periodos.forEach(periodo => {
      const gmv = this.getUEValor(groupedData, fechas, periodo, tipo, 'gmv');
      const orders = this.getUEValor(groupedData, fechas, periodo, tipo, 'total_orders') || 1;
      aovRow[periodo] = orders > 0 ? +(gmv / orders).toFixed(0) : 0;
    });
    rows.push(aovRow);

    // Margen Bruto %
    const margenRow: any = { 'Indicador': 'Margen Bruto %' };
    periodos.forEach(periodo => {
      const gmv = this.getUEValor(groupedData, fechas, periodo, tipo, 'gmv');
      const cogs = this.getUEValor(groupedData, fechas, periodo, tipo, 'cogs');
      margenRow[periodo] = gmv ? +((1 - (cogs * -1 / gmv)) * 100).toFixed(2) : 0;
    });
    rows.push(margenRow);

    // Utilidad Neta
    const utilidadRow: any = { 'Indicador': 'Utilidad Neta' };
    periodos.forEach(periodo => {
      const gmv = this.getUEValor(groupedData, fechas, periodo, tipo, 'gmv');
      const cogs = this.getUEValor(groupedData, fechas, periodo, tipo, 'cogs');
      const log = this.getUEValor(groupedData, fechas, periodo, tipo, 'logistics_cost');
      const pers = this.getUEValor(groupedData, fechas, periodo, tipo, 'perssonel');
      const tech = this.getUEValor(groupedData, fechas, periodo, tipo, 'cost_tech');
      const others = this.getUEValor(groupedData, fechas, periodo, tipo, 'cost_others');
      utilidadRow[periodo] = gmv + cogs + log + pers + tech + others;
    });
    rows.push(utilidadRow);

    return rows;
  }

  private getUEValor(groupedData: { [fecha: string]: any[] }, fechas: string[], periodo: string, tipo: 'mes' | 'semana' | 'dia', variable: string): number {
    return fechas
      .filter(f =>
        tipo === 'mes' ? f.startsWith(periodo) :
        tipo === 'semana' ? this.getSemanaISO(f) === periodo :
        f === periodo
      )
      .flatMap(f => groupedData[f] || [])
      .filter(e => e.variable === variable)
      .reduce((sum, e) => sum + (e.valor || 0), 0);
  }

  private getSemanaISO(fecha: string): string {
    const d = new Date(fecha);
    const y = d.getFullYear();
    const w = this.getISOWeek(d);
    return `${y}-W${w.toString().padStart(2, '0')}`;
  }

  private getISOWeek(d: Date): number {
    const date = new Date(d.getTime());
    date.setUTCDate(date.getUTCDate() + 4 - (date.getUTCDay() || 7));
    const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
    return Math.ceil((((date.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
  }
}
