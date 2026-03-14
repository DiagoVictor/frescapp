import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
@Injectable({
  providedIn: 'root'
})
export class ProductsAnalyticsService {
  private baseUrl = environment.apiUrl;

  constructor(private httpClient: HttpClient) { }

  getProducts(): Observable<any[]> {
    return this.httpClient.get<any[]>(this.baseUrl+'api/products_history/products_history_analytics');
  }
}
