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
  updateRoute(cliente: any)  {
    return this.http.put(`${this.baseUrl}/${cliente._id}`, cliente);
  }

  delteRoute(routeNumber: string) {
    return this.http.delete(this.baseUrl +'route/route/'+ routeNumber);
  }
  createRoute(date:string,conductor:string){
    return this.http.post<any>(this.baseUrl+'api/route/route',{close_date : date, driver: conductor});
  }
  updateStop(data:any): Observable<any[]> {
    return this.http.put<any[]>(`${this.baseUrl}route/stop`, data);
  }
  getstops(route_id:any): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}route/stops/${route_id}`);
  }
}
