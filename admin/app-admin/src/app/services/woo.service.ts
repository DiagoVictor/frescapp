import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class WooService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  constructor(private http: HttpClient) { }
  get_order(order_number:any){
    console.log(order_number)
    return this.http.get(this.baseUrl+'api/woo/get_order/'+order_number);
  }
}
