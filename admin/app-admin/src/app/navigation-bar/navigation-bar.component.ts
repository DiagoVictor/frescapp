import { Component, OnInit } from '@angular/core';
import { AuthenticationService } from '../services/authentication.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-navigation-bar',
  templateUrl: './navigation-bar.component.html',
  styleUrls: ['./navigation-bar.component.css']
})
export class NavigationBarComponent implements OnInit {

  constructor(private authService: AuthenticationService, private router: Router) { }
  role:string | null ='';
  ngOnInit(): void {
  }

  isLoggedIn(): boolean {
    const token = localStorage.getItem('token');
    this.role = localStorage.getItem('role');
    return !!token; 
  }
  isMenuCollapsed = true;

  toggleMenu() {
    this.isMenuCollapsed = !this.isMenuCollapsed;
  }
  logout(): void {
    const token = localStorage.getItem('token');
    if (token) {
      this.authService.logout(token).subscribe(
        () => {
          localStorage.removeItem('token');
          this.router.navigate(['/login']);
        },
        error => {
          this.router.navigate(['/login']);
        }
      );
    } else {
      this.router.navigate(['/login']);
    }
  }
}
