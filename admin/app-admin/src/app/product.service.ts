import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private baseUrl = 'http://127.0.0.1:5000/';

  constructor(private httpClient: HttpClient) { }

  getProducts(): Observable<any[]> {
    return this.httpClient.get<any[]>(this.baseUrl+'api/product/products');
  }
  updateProduct(product_id:any,product_data:any): Observable<any[]> {
    return this.httpClient.put<any[]>(this.baseUrl + 'api/product/products/'+product_id,product_data);
  }
  createProduct(product_data:any): Observable<any[]> {
    return this.httpClient.post<any[]>(this.baseUrl + 'api/product/product',product_data);
  }
}
