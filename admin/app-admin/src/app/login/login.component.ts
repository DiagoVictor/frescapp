import { Component } from '@angular/core';
import { AuthenticationService } from '../authentication.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  username: string = '';
  password: string = '';

  constructor(private authService: AuthenticationService, private router: Router) {}

  login() {
    // Verificar si los campos están vacíos
    if (this.username === '' || this.password === '') {
      alert('Por favor, ingrese nombre de usuario y contraseña.');
      return;
    }

    // Llamar al método de inicio de sesión del servicio de autenticación
    this.authService.login(this.username, this.password)
      .subscribe(
        () => {
          this.router.navigate(['/home']);
        },
        (        error: any) => {
          console.error('Error al iniciar sesión:', error);
          alert('Nombre de usuario o contraseña incorrectos.');
        }
      );
  }
}
