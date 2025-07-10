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
  fechaInicio: string = '';
  fechaFin: string = '';

  constructor(private unitEconomicsService: UnitEconomicsService) {}

  ngOnInit(): void {
    this.unitEconomicsService.getUnitEconomics().subscribe(data => {
      this.groupedData = this.groupByDate(data);
      this.loading = false;
      console.log('Unit Economics Data:', this.groupedData);
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
    }, {} as { [fecha: string]: UnitEconomicEntry[] });
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
    this.getFechas().forEach(f => meses.add(f.slice(0, 7))); // yyyy-MM
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
