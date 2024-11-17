import { Component, OnInit } from '@angular/core';
import { UnitEconomicsService } from '../services/unit-economics.service';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.css']
})
export class ReportsComponent implements OnInit {
  ueDate: string = '';
  monthlyData: any = {};
  weeklyData: any = {};
  selectedPeriod: string = '';
  semanas: string[] = ['Semana 40', 'Semana 41', 'Semana 42', 'Semana 43', 'Semana 44'];
  meses: string[] = ['Octubre', 'Noviembre']
  constructor(private unitEconomicsService: UnitEconomicsService) { }

  ngOnInit(): void {
    this.getUE();
  }
  // Función para actualizar los datos de la UE
  updateUnitEconomics() {
    this.unitEconomicsService.updateUE(this.ueDate).subscribe(
      response => {
        this.getUE(); // Refresca los datos después de la actualización
      },
      error => {
        console.error('Error al actualizar la UE:', error);
      }
    );
  }

  // Función para obtener los datos de las unidades económicas
  getUE() {
    this.unitEconomicsService.getUE('Mensual').subscribe(
      response => {
        this.monthlyData = this.pivotData(response); // Pivotar los datos mensuales
      },
      error => {
        console.error('Error al obtener los datos de la UE mensual:', error);
      }
    );

    this.unitEconomicsService.getUE('Semanal').subscribe(
      response => {
        this.weeklyData = this.pivotData(response);
      },
      error => {
        console.error('Error al obtener los datos de la UE semanal:', error);
      }
    );
  }

  // Función para pivotar los datos y convertir métricas en filas
  pivotData(data: any[]): any {
    const pivotedData: any = {};

    data.forEach(item => {
      const tipo = item.tipo; // Ej. mensual o semanal
      const periodo = item.periodo; // Ej. octubre

      Object.keys(item).forEach(metric => {
        // Ignorar los campos no relacionados con métricas
        if (['tipo', 'periodo', '_id', 'year'].includes(metric)) return;

        // Crear una estructura anidada para cada métrica en `pivotedData`
        if (!pivotedData[metric]) {
          pivotedData[metric] = {}; // Crear objeto para la métrica
        }

        if (!pivotedData[metric][tipo]) {
          pivotedData[metric][tipo] = {}; // Crear objeto para el tipo (mensual/semanal)
        }

        pivotedData[metric][tipo][periodo] = item[metric]; // Asignar valor según tipo y periodo
      });
    });
    return pivotedData;
  }

}
