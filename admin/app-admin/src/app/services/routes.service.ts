import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
@Injectable({
  providedIn: 'root'
})
export class RoutesService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  //private baseUrl = 'http://localhost:5000/';
  constructor(private http: HttpClient) { }
  getRoutes():Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/route/routes');
  }
  getRoute(routeNumber:any):Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/route/route/'+routeNumber);
  }
  updateRoute(route: any) {
    return this.http.put<any>(this.baseUrl+'api/route/route', {'route' : route, 'evidence': ''});
  }
  updateStop(route: any, evidence: File | null) {
    const formData = new FormData();
    
    // Agregar la información de la ruta como un string JSON
    formData.append('route', JSON.stringify(route));
    
    // Agregar el archivo de evidencia si existe
    if (evidence) {
      formData.append('evidence', evidence, evidence.name);
    }
  
    // Enviar la solicitud PUT
    return this.http.put<any>(`${this.baseUrl}api/route/route`, formData);
  }
  
  delteRoute(route_id: string) {
    return this.http.delete(this.baseUrl +'api/route/route/'+ route_id);
  }
  createRoute(date:string,conductor:string,costo:number){
    return this.http.post<any>(this.baseUrl+'api/route/route',{close_date : date, driver: conductor, cost: costo});
  }
}
