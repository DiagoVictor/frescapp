import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ClientesService {
  private baseUrl = 'http://3.23.102.32:5000/';
  constructor(private httpClient: HttpClient) { }

  getClientes() {
    return this.httpClient.get<any[]>(this.baseUrl+'api/customer/customers');
  }
}
