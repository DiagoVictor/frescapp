import { Component, OnInit } from '@angular/core';
import { UnitEconomicsService } from '../services/unit-economics.service';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.css']
})
export class ReportsComponent implements OnInit {
  ueData = {
    fecha_base: '',
    wh_rent: null,
    cost_tech: null,
    sales_force: null,
    otros_costos: null,
    cost_insumos: null
  };

  // Variables para almacenar los datos pivotados
  monthlyData: any = {};
  weeklyData: any = {};
  selectedPeriod: string = '';
  semanas: string[] = ['semana 40','semana 41','semana 42','semana 43','semana 44']; 
  meses: string[] = ['octubre','noviembre']
  constructor(private unitEconomicsService: UnitEconomicsService) {}

  ngOnInit(): void {
    this.getUE(); 
  }
  // Función para actualizar los datos de la UE
  updateUnitEconomics() {
    const dataToSend = {
      dateUpdate: this.ueData.fecha_base,
      wh_rent: this.ueData.wh_rent,
      cost_tech: this.ueData.cost_tech,
      sales_force: this.ueData.sales_force,
      otros_costos: this.ueData.otros_costos,
      cost_insumos: this.ueData.cost_insumos
    };

    this.unitEconomicsService.updateUE(dataToSend).subscribe(
      response => {
        console.log('UE Actualizada:', response);
        this.getUE(); // Refresca los datos después de la actualización
      },
      error => {
        console.error('Error al actualizar la UE:', error);
      }
    );
  }

  // Función para obtener los datos de las unidades económicas
  getUE() {
    this.unitEconomicsService.getUE('mensual').subscribe(
      response => {
        this.monthlyData = this.pivotData(response); // Pivotar los datos mensuales
      },
      error => {
        console.error('Error al obtener los datos de la UE mensual:', error);
      }
    );

    this.unitEconomicsService.getUE('semanal').subscribe(
      response => {
        this.weeklyData = this.pivotData(response); // Pivotar los datos semanales
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
    console.log(pivotedData)
    return pivotedData;
}

}
