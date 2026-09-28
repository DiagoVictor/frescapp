import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
@Injectable({
  providedIn: 'root'
})
export class CostsService {
  private baseUrl = environment.apiUrl;
  constructor(private http: HttpClient) { }
  getCostos():Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/cost/cost');
  }
  updateCosto(costo: any) {
    return this.http.put<any>(this.baseUrl+'api/cost/cost', costo);
  }

  deleteCosto(cost_id: string) {
    return this.http.delete(this.baseUrl +'api/cost/cost/'+ cost_id);
  }
  createCosto(costo:any){
    return this.http.post<any>(this.baseUrl+'api/cost/cost',costo);
  }
}
