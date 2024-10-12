import { Component } from '@angular/core';
import { RoutesService } from '../../services/routes.service';

@Component({
  selector: 'app-list-rutas',
  templateUrl: './list-rutas.component.html',
  styleUrl: './list-rutas.component.css'
})
export class ListRutasComponent {
  public filteredRoutes:any = [];
  public routes:any = [];
  public searchText = '';
  public messageRoute = '';
  public newRouteDate: string = '';
  public newRouteDriver: string = '';
  public drivers: string[] = ['Carlos Julio Lopez']


  constructor(
    private routesService: RoutesService,

  ) { }

  ngOnInit(): void {
    this.getRoutes();
    this.filteredRoutes = this.routes;
    console.log(this.filteredRoutes)
  }
  getRoutes(){
    this.routesService.getRoutes().subscribe(
      (res: any) => {
        this.routes = res;
      }
      )
  }
  filterRoutes() {
    //this.filteredRoutes = this.routes.filter(route => route.date.includes(this.searchText));
  }

  createRoute() {
    this.routesService.createRoute(this.newRouteDate,this.newRouteDriver).subscribe(
      (res: any) => {
        this.messageRoute = 'Nueva ruta creada exitosamente!';
        this.getRoutes();
        this.filteredRoutes = this.routes;
      }
    )
  }

  deleteRoute(routeId: number) {
    //this.routes = this.routes.filter(route => route.id !== routeId);
    this.filteredRoutes = this.routes;
    this.messageRoute = 'Ruta eliminada exitosamente!';
  }

  navigateToRoute(routeId: number) {
    // Implementar navegación a detalles de la ruta
  }
  programarRuta(route:any){

  }
  calculateTotalToCharge() {
    this.filteredRoutes.forEach((route: any) => {
      let total = 0;
      route.stops.forEach((stop: any) => {
        total += stop.total_to_charge; // Sumar el total a cobrar de cada parada
      });
      route.total_to_charge = total; // Agregar el total a la ruta
    });
  }

  // Función para calcular la cantidad de paradas por ruta
  calculateTotalStops() {
    this.filteredRoutes.forEach((route: any) => {
      const totalStops = route.stops.length; // Contar la cantidad de paradas
      route.total_stops = totalStops; // Agregar la cantidad de paradas a la ruta
    });
  }

}
