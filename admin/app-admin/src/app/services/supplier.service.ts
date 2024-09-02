import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SupplierService {
  private baseUrl = 'https://app.buyfrescapp.com:5000/';
  //private baseUrl = 'https://localhost:5000/';
  constructor(private http: HttpClient) { }
  getSuppliers() {
    return this.http.get(this.baseUrl);
  }

  createSupplier(supplier: any) {
    return this.http.post(this.baseUrl, supplier);
  }

  updateSupplier(supplier: any) {
    return this.http.put(`${this.baseUrl}/${supplier.id}`, supplier);
  }

  deleteSupplier(supplierId: number) {
    return this.http.delete(`${this.baseUrl}/${supplierId}`);
  }
}
