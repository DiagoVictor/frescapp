import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, map } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {
  private baseUrl = 'http://3.23.102.32:5000/';

  constructor(private http: HttpClient) { }

  login(username: string, password: string): Observable<any> {
    return this.http.post<any>(this.baseUrl + 'api/user/login', { 'user': username, 'password': password })
      .pipe(
        // Al recibir la respuesta del servidor, guardar el token en el almacenamiento local
        map(response => {
          if (response.token) {
            localStorage.setItem('token', response.token);
          }
          return response;
        })
      );
  }

  logout(token: string): Observable<any> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Authorization': `Bearer ${token}`
      })
    };
    return this.http.post<any>(this.baseUrl+'api/user/logout', {}, httpOptions);
  }

  checkToken(token: string): Observable<any> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Authorization': `Bearer ${token}`
      })
    };
    return this.http.post<any>(this.baseUrl+'api/user/check_token', {}, httpOptions);
  }

  changePassword(token: string, newPassword: string): Observable<any> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Authorization': `Bearer ${token}`
      })
    };
    return this.http.post<any>(this.baseUrl+'api/user/change_password', { password: newPassword }, httpOptions);
  }
}
