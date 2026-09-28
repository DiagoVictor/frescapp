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

  // Resoluciones de facturación
  get_resolutions() {
    return this.http.get<any[]>(this.baseUrl+'api/alegra/resolutions');
  }
  get_active_resolution() {
    return this.http.get<any>(this.baseUrl+'api/alegra/resolutions/active');
  }
  create_resolution(data: any) {
    return this.http.post<any>(this.baseUrl+'api/alegra/resolutions', data);
  }
  update_resolution(id: string, data: any) {
    return this.http.put<any>(this.baseUrl+'api/alegra/resolutions/'+id, data);
  }
  activate_resolution(id: string) {
    return this.http.post<any>(this.baseUrl+'api/alegra/resolutions/'+id+'/activate', {});
  }
  delete_resolution(id: string) {
    return this.http.delete<any>(this.baseUrl+'api/alegra/resolutions/'+id);
  }
  get_number_templates() {
    return this.http.get<any[]>(this.baseUrl+'api/alegra/number_templates');
  }

  // Facturas pendientes por emitir
  get_pending_invoices(days: number) {
    return this.http.get<any>(this.baseUrl+'api/alegra/pending_invoices?days='+days);
  }
  send_pending_invoices(days: number) {
    return this.http.post<any>(this.baseUrl+'api/alegra/pending_invoices', { days });
  }
}
