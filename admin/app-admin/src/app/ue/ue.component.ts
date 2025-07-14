import { Component, OnInit } from '@angular/core';
import { UnitEconomicsService } from '../services/unit-economics.service';

interface UnitEconomicEntry {
  detalle: string;
  fecha: string;
  valor: number;
  variable: string;
}

@Component({
  selector: 'app-ue',
  templateUrl: './ue.component.html',
  styleUrls: ['./ue.component.css']
})
export class UeComponent implements OnInit {
  groupedData: { [fecha: string]: UnitEconomicEntry[] } = {};
  loading = true;
  fechaInicio: string = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  fechaFin: string = new Date().toISOString().split('T')[0];


  indicadores = [
    { key: 'gmv', label: 'GMV' },
    { key: 'cogs', label: 'COGS' },
    { key: 'cost_others', label: 'Otros Costos' },
    { key: 'logistics_cost', label: 'Logística' },
    { key: 'perssonel', label: 'Personal' },
    { key: 'cost_tech', label: 'Tecnología' },
    { key: 'total_orders', label: 'Órdenes' },
    { key: 'total_lines', label: 'Líneas' },
  ];

  constructor(private unitEconomicsService: UnitEconomicsService) {}

  ngOnInit(): void {
    this.unitEconomicsService.getUnitEconomics().subscribe(data => {
      this.groupedData = this.groupByDate(data);
      this.loading = false;
    }, error => {
      console.error('Error fetching unit economics data:', error);
      this.loading = false;
    });
  }

  groupByDate(data: UnitEconomicEntry[]): { [fecha: string]: UnitEconomicEntry[] } {
    return data.reduce((acc: { [fecha: string]: UnitEconomicEntry[] }, item) => {
      const fecha = item.fecha;
      if (!acc[fecha]) acc[fecha] = [];
      acc[fecha].push(item);
      return acc;
    }, {});
  }

  getResumen(entries: UnitEconomicEntry[], variable: string): number {
    return entries.filter(e => e.variable === variable)
                  .reduce((sum, e) => sum + e.valor, 0);
  }

  getUtilidad(entries: UnitEconomicEntry[]): number {
    return ['gmv', 'cogs', 'cost_others', 'logistics_cost', 'perssonel', 'cost_tech']
      .map(v => this.getResumen(entries, v))
      .reduce((a, b) => a + b, 0);
  }

  getMargen(entries: UnitEconomicEntry[]): string {
    const gmv = this.getResumen(entries, 'gmv');
    const utilidad = this.getUtilidad(entries);
    return gmv !== 0 ? ((utilidad / gmv) * 100).toFixed(2) + '%' : 'N/A';
  }

  getMargenBruto(entries: UnitEconomicEntry[]): string {
    const gmv = this.getResumen(entries, 'gmv');
    const cogs = this.getResumen(entries, 'cogs');
    if (gmv === 0) return 'N/A';
    return ((1-(cogs*-1 / gmv)) * 100).toFixed(2) + '%';
  }

  getMargenLogistico(entries: UnitEconomicEntry[]): string {
    const gmv = this.getResumen(entries, 'gmv');
    const logistics = this.getResumen(entries, 'logistics_cost');
    if (gmv === 0) return 'N/A';
    return ((logistics / gmv) * 100).toFixed(2) + '%';
  }

  getMargenBrutoMensual(mes: string): string {
    const gmv = this.getResumenMensual(mes, 'gmv');
    const cogs = this.getResumenMensual(mes, 'cogs');
    return gmv !== 0 ? ((1-((cogs*-1 / gmv))) * 100).toFixed(2) + '%' : 'N/A';
  }
  getMargenBrutoSemanal(semana: string): string {
    const gmv = this.getResumenSemanal(semana, 'gmv');
    const cogs = this.getResumenSemanal(semana, 'cogs');
    return gmv !== 0 ? ((1-((cogs*-1 / gmv))) * 100).toFixed(2) + '%' : 'N/A';
  }
  getMargenLogisticoMensual(mes: string): string {
    const gmv = this.getResumenMensual(mes, 'gmv');
    const logistics = this.getResumenMensual(mes, 'logistics_cost');
    return gmv !== 0 ? ((logistics / gmv) * 100).toFixed(2) + '%' : 'N/A';
  }
  getMargenLogisticoSemanal(semana: string): string {
    const gmv = this.getResumenSemanal(semana, 'gmv');
    const logistics = this.getResumenSemanal(semana, 'logistics_cost');
    return gmv !== 0 ? ((logistics / gmv) * 100).toFixed(2) + '%' : 'N/A';
  }
  getAOVMensual(mes: string): string {
    const gmv = this.getResumenMensual(mes, 'gmv');
    const orders = this.getResumenMensual(mes, 'total_orders');
    return orders !== 0 ? (gmv / orders).toFixed(0) : 'N/A';
  }
  getAOVSemanal(semana: string): string {
    const gmv = this.getResumenSemanal(semana, 'gmv');
    const orders = this.getResumenSemanal(semana, 'total_orders');
    return orders !== 0 ? (gmv / orders).toFixed(0) : 'N/A';
  }
  getAOLMensual(mes: string): string {
    const gmv = this.getResumenMensual(mes, 'gmv');
    const lines = this.getResumenMensual(mes, 'total_lines');
    return lines !== 0 ? (gmv / lines).toFixed(2) : 'N/A';
  }
  getAOLSemanal(semana: string): string {
    const gmv = this.getResumenSemanal(semana, 'gmv');
    const lines = this.getResumenSemanal(semana, 'total_lines');
    return lines !== 0 ? (gmv / lines).toFixed(2) : 'N/A';
  }
  getAOV(entries: UnitEconomicEntry[]): string {
    const gmv = this.getResumen(entries, 'gmv');
    const orders = this.getResumen(entries, 'total_orders');
    if (orders === 0) return 'N/A';
    return (gmv / orders).toFixed(0);
  }

  getAOL(entries: UnitEconomicEntry[]): string {
    const lines = this.getResumen(entries, 'total_lines');
    const gmv = this.getResumen(entries, 'gmv');
    if (lines === 0) return 'N/A';
    return (gmv / lines).toFixed(2);
  }

  getFechas(): string[] {
    return Object.keys(this.groupedData).sort();
  }

  getFechasFiltradas(): string[] {
    const start = new Date(this.fechaInicio);
    const end = new Date(this.fechaFin);
    return this.getFechas().filter(f => {
      const d = new Date(f);
      return (!this.fechaInicio || d >= start) && (!this.fechaFin || d <= end);
    });
  }

  getMeses(): string[] {
    const meses = new Set<string>();
    this.getFechas().forEach(f => meses.add(f.slice(0, 7)));
    return Array.from(meses).sort();
  }

  getResumenMensual(mes: string, variable: string): number {
    return this.getFechas()
      .filter(f => f.startsWith(mes))
      .flatMap(f => this.groupedData[f])
      .filter(e => e.variable === variable)
      .reduce((sum, e) => sum + e.valor, 0);
  }

  getUtilidadMensual(mes: string): number {
    return ['gmv', 'cogs', 'cost_others', 'logistics_cost', 'perssonel', 'cost_tech']
      .map(v => this.getResumenMensual(mes, v))
      .reduce((a, b) => a + b, 0);
  }

  getMargenMensual(mes: string): string {
    const gmv = this.getResumenMensual(mes, 'gmv');
    const utilidad = this.getUtilidadMensual(mes);
    return gmv !== 0 ? ((utilidad / gmv) * 100).toFixed(2) + '%' : 'N/A';
  }

  getSemanas(): string[] {
    const semanas = new Set<string>();
    this.getFechas().forEach(f => {
      const d = new Date(f);
      const y = d.getFullYear();
      const week = this.getISOWeek(d);
      semanas.add(`${y}-W${week.toString().padStart(2, '0')}`);
    });
    return Array.from(semanas).sort();
  }

  getResumenSemanal(semana: string, variable: string): number {
    return this.getFechas()
      .filter(f => this.getSemanaISO(f) === semana)
      .flatMap(f => this.groupedData[f])
      .filter(e => e.variable === variable)
      .reduce((sum, e) => sum + e.valor, 0);
  }

  getUtilidadSemanal(semana: string): number {
    return ['gmv', 'cogs', 'cost_others', 'logistics_cost', 'perssonel', 'cost_tech']
      .map(v => this.getResumenSemanal(semana, v))
      .reduce((a, b) => a + b, 0);
  }

  getMargenSemanal(semana: string): string {
    const gmv = this.getResumenSemanal(semana, 'gmv');
    const utilidad = this.getUtilidadSemanal(semana);
    return gmv !== 0 ? ((utilidad / gmv) * 100).toFixed(2) + '%' : 'N/A';
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
    const weekNo = Math.ceil((((date.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
    return weekNo;
  }
}
