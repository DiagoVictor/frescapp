import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ClientesService {
  private baseUrl = environment.apiUrl;
  constructor(private http: HttpClient) { }
  getClientes() {
    return this.http.get<any[]>(this.baseUrl+'api/customer/customers');
  }
  createCliente(cliente: any)  {
    return this.http.post(`${this.baseUrl}api/customer/customer`, cliente);
  }

  updateCliente(cliente: any)  {
    return this.http.put(`${this.baseUrl}api/customer/customers/${cliente.id}`, cliente);
  }

  deleteCliente(id: string) {
    return this.http.delete(`${this.baseUrl}/${id}`);
  }
  changePassword(id: string, password: string): Observable<any> {
    return this.http.post(this.baseUrl+'api/user/change_password_admin', {user_id : id, password: password});

  }
}
