import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
@Injectable({
  providedIn: 'root'
})
export class CierresService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  //private baseUrl = 'http://localhost:5000/';
  constructor(private http: HttpClient) { }
  getCierres():Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/cierres');
  }
  getCierre(id:string):Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/cierres/'+id);
  }
  updateCierre(cierre:any)  {
    return this.http.put(`${this.baseUrl}/api/cierres/${cierre.id}`, cierre);
  }

  deleteCierre(id: string) {
    return this.http.delete(this.baseUrl +'api/cierres/'+ id);
  }
  createCierre(close_date:any){
    return this.http.post<any[]>(this.baseUrl+'api/cierres/'+close_date,{});
  }
}
