import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AlegraService {
  private baseUrl = environment.apiUrl;


  constructor(private http: HttpClient) { }
  send_invoice(order_number:any) {
    return this.http.get(this.baseUrl+'api/alegra/send_invoice/'+order_number);
  }
  get_invoice(order_number: any) {
    return this.http.get(this.baseUrl+'api/alegra/get_invoice/'+order_number);
  }
  send_purchase(fecha:any){
    return this.http.get(this.baseUrl+'api/alegra/send_purchase/'+fecha);
  }
}
