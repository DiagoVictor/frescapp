import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ClientesService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  constructor(private http: HttpClient) { }
  getClientes() {
    return this.http.get<any[]>(this.baseUrl+'api/customer/customers');
  }
  createCliente(cliente: any)  {
    return this.http.post(`${this.baseUrl}`, cliente);
  }

  updateCliente(cliente: any)  {
    return this.http.put(`${this.baseUrl}/${cliente._id}`, cliente);
  }

  deleteCliente(id: string) {
    return this.http.delete(`${this.baseUrl}/${id}`);
  }
}
