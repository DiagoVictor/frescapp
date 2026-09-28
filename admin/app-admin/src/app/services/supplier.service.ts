import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SupplierService {
  private baseUrl = environment.apiUrl;
  constructor(private http: HttpClient) { }
  getSuppliers():Observable<any> {
    return this.http.get(`${this.baseUrl}api/supplier/suppliers`);
  }

  createSupplier(supplier: any):Observable<any> {
    return this.http.post(`${this.baseUrl}api/supplier/supplier`, supplier);
  }

  updateSupplier(supplier: any):Observable<any> {
    return this.http.put(`${this.baseUrl}api/supplier/supplier/${supplier._id}`, supplier);
  }

  deleteSupplier(supplierId: number):Observable<any> {
    return this.http.delete(`${this.baseUrl}api/supplier/supplier/${supplierId}`);
  }
}
