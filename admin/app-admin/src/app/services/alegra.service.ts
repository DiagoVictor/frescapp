import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class AlegraService {
  private baseUrl = 'http://app.buyfrescapp.com:5000/';
  //private baseUrl = 'http://127.0.0.1:5000/';


  constructor(private http: HttpClient) { }
  send_invoice(order_number:any) {
    return this.http.get(this.baseUrl+'api/alegra/send_invoice/'+order_number);
  }
  get_invoice(id: any) {
    const url = `https://api.alegra.com/api/v1/invoices/215/open`;
    const headers = new HttpHeaders({
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Basic dm1kaWFnb3ZAZ21haWwuY29tOjBmZmQ1YzdiM2NiMWI5OWVjNDA0',
      // Agregar cualquier encabezado adicional necesario
      'X-Authorization': 'tu-valor',
      'Origin': 'tu-origen', // Reemplaza 'tu-origen' con el valor apropiado
      'X-Requested-With': 'XMLHttpRequest',
      'X-HTTP-Method-Override': 'POST', // Solo si necesitas sobrescribir el método
      // Encabezados personalizados opcionales
      'X-Data-Source': 'tu-data-source',
      'X-Experiment-Onb-Variant': 'tu-variant',
      'X-Experiment-Onb-Id': 'tu-id',
      'X-Request-Origin-Project': 'tu-proyecto',
      'X-School-Name': 'tu-school-name',
      'X-Regime-Name': 'tu-regime-name',
      'X-Sat-Register': 'tu-sat-register'
    });
    return this.http.post(url, { headers: headers });
  }
}
