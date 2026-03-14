import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class WooService {
  private baseUrl = environment.apiUrl;
  constructor(private http: HttpClient) { }
  get_order(order_number:any){
    return this.http.get(this.baseUrl+'api/woo/get_order/'+order_number);
  }
}
