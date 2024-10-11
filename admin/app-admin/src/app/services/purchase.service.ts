import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PurchaseService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  //private baseUrl = 'http://localhost:5000/';
  constructor(private http: HttpClient) { }
  getPurchases():Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/purchase/purchases');
  }
  getPurchase(purchaseNumber:any):Observable<any> {
    return this.http.get<any[]>(this.baseUrl+'api/purchase/purchase/'+purchaseNumber);
  }
  updatePurchase(cliente: any)  {
    return this.http.put(`${this.baseUrl}/${cliente._id}`, cliente);
  }

  deletePurchase(purchase_number: string) {
    return this.http.delete(this.baseUrl +'api/purchase/purchase/'+ purchase_number);
  }
  createPurchase(date:any){
    return this.http.get<any[]>(this.baseUrl+'api/purchase/create/'+date);
  }
  updatePrice(data:any): Observable<any[]> {
    return this.http.post<any[]>(`${this.baseUrl}api/purchase/update_price`, data);
  }
  getReport(purchase_number: string){
    return `${this.baseUrl}api/purchase/purchase/report/${purchase_number}`;
  }
}
