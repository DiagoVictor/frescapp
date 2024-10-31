import { Component } from '@angular/core';
import { RoutesService } from '../../services/routes.service';
import { Router } from '@angular/router';

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
  public newCost : number = 0;
  public drivers: string[] = ['Carlos Julio Lopez']


  constructor(
    private routesService: RoutesService,
    private router: Router,

  ) { }

  ngOnInit(): void {
    this.getRoutes();
    //this.filterRoutes();
  }
  getRoutes(){
    this.routesService.getRoutes().subscribe(
      (res: any) => {
        this.routes = res;
        this.filteredRoutes = this.routes;
      }
      )
  }
  filterRoutes() {
    //this.filteredRoutes = this.routes.filter(route => route.date.includes(this.searchText));
  }

  createRoute() {
    this.routesService.createRoute(this.newRouteDate,this.newRouteDriver,this.newCost).subscribe(
      (res: any) => {
        this.messageRoute = 'Nueva ruta creada exitosamente!';
        this.getRoutes();
        this.filteredRoutes = this.routes;
      }
    )
  }

  deleteRoute(route : any) {
    this.routesService.delteRoute(route.id).subscribe(
      (res: any) => {
        this.messageRoute = 'Ruta eliminada exitosamente!';
        this.getRoutes();
        this.filteredRoutes = this.routes;
      }
    )
  }

  navigateToRoute(routNumber: number) {
    this.router.navigate(['/stops', routNumber]);
  }
  programarRuta(route:any){

  }
  calculateTotalToCharge(routeId: string) {
    const route = this.filteredRoutes.find((route: any) => route.id === routeId);
    if (route) {
      let total = 0;
      route.stops.forEach((stop: any) => {
        total += stop.total_to_charge; // Sumar el total a cobrar de cada parada
      });
      return total; 
    }
    return 0
  }
  
  calculateTotalStops(routeId: string) {
    const route = this.filteredRoutes.find((route: any) => route.id === routeId);
    if (route) {
      return route.stops.length; 
    }
    return 0
  }
}
