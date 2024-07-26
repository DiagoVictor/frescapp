import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PurchaseService {
  //private baseUrl = 'http://app.buyfrescapp.com:5000/';
  private baseUrl = 'http://localhost:5000/';
  constructor(private http: HttpClient) { }
  getPurchases():Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/purchase/purchases');
  }
  updatePurchase(cliente: any)  {
    return this.http.put(`${this.baseUrl}/${cliente._id}`, cliente);
  }

  deletePurchase(id: string) {
    return this.http.delete(`${this.baseUrl}/${id}`);
  }
  createPurchase(date:any){
    return this.http.get<any[]>(this.baseUrl+'api/purchase/purchase/'+date);
  }
}
