import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class OrderService {
  private baseUrl = 'http://app.buyfrescapp.com:5000/';

  constructor(private http: HttpClient) { }

  getOrders(): Observable<any[]> {
    return this.http.get<any[]>(this.baseUrl+'api/order/orders');
  }

  updateOrder(orderId: number, orderData: any): Observable<any> {
    const url = this.baseUrl + 'api/order/order/' + orderId;
    return this.http.post(url, orderData);
  }

  createOrder(orderData: any): Observable<any> {
    return this.http.post(this.baseUrl+'api/order/order', orderData);
  }
  getConfig(): Observable<any> {
      return this.http.get<any>(this.baseUrl+ 'api/config/configOrder');
  }
}
