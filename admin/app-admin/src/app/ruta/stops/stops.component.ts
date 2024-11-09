import { Component } from '@angular/core';
import { RoutesService } from '../../services/routes.service';
import { Router } from '@angular/router';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-stops',
  templateUrl: './stops.component.html',
  styleUrl: './stops.component.css'
})
export class StopsComponent {
  public stops: any = [];
  public routeNumber: number = 0;
  public routeSelect: any;
  public stopSelect: any;
  public methedoPayments = ["Nequi Carlos", "Daviplata Carlos", "Consignación Bancaria", "Mercado pago", "Efectivo"];
  public statusStops = ["Por entregar", "Pendiente de pago", "Pagada"];

  constructor(
    private routesService: RoutesService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.route.params.subscribe(params => {
      this.routeNumber = params['route_number'];
    });
  }

  ngOnInit(): void {
    this.getStops();
  }

  getStops() {
    this.routesService.getRoute(this.routeNumber).subscribe(
      (res: any) => {
        this.routeSelect = res;
    
        // Ordena los stops basados en el atributo 'order'
        this.stops = res["stops"].sort((a: any, b: any) => a.order - b.order);
    
        // Selecciona el primer stop después de ordenar
        this.stopSelect = this.stops[0];
      }
    );    
  }

  navigateToStop(stop: any) {
    this.stopSelect = stop;
  }

  saveStop() {
    // Encuentra el índice del stop actual en el array de stops
    const index = this.stops.findIndex((s: any) => s.order === this.stopSelect.order);
    
    // Actualiza el stop en el array de stops de la ruta
    if (index !== -1) {
      this.routeSelect.stops[index] = this.stopSelect;
    }

    // Llama al servicio para actualizar la ruta completa con el stop modificado
    this.routesService.updateRoute(this.routeSelect).subscribe(
      (response: any) => {
        console.log("Parada guardada y ruta actualizada", response);
      },
      (error: any) => {
        console.error("Error al guardar la parada", error);
      }
    );
  }
  navigateToRoute(){
    this.router.navigate(['/rutas']);
  }
}
