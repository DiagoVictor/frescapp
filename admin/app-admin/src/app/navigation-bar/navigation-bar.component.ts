import { Component, OnInit } from '@angular/core';
import { AuthenticationService } from '../authentication.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-navigation-bar',
  templateUrl: './navigation-bar.component.html',
  styleUrls: ['./navigation-bar.component.css']
})
export class NavigationBarComponent implements OnInit {

  constructor(private authService: AuthenticationService, private router: Router) { }

  ngOnInit(): void {
  }

  isLoggedIn(): boolean {
    // Implementa tu lógica para verificar si el usuario está autenticado
    // Por ejemplo, podrías verificar si existe un token de autenticación en el almacenamiento local
    const token = localStorage.getItem('token');
    return !!token; // Devuelve true si hay un token, de lo contrario false
  }

  logout(): void {
    // Obtener el token del almacenamiento local
    const token = localStorage.getItem('token');

    // Verificar si hay un token antes de intentar cerrar sesión
    if (token) {
      // Llamar al método logout del AuthenticationService para cerrar la sesión
      this.authService.logout(token).subscribe(
        () => {
          // Eliminar el token del almacenamiento local después de cerrar sesión correctamente
          localStorage.removeItem('token');
          this.router.navigate(['/login']);
        },
        error => {
          // Manejar cualquier error que pueda ocurrir durante el proceso de cierre de sesión
          this.router.navigate(['/login']);
        }
      );
    } else {
      this.router.navigate(['/login']);
    }
  }
}
