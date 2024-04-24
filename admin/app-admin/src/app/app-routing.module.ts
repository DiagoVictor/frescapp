import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ProductsComponent } from './products/products.component'; // Importa el componente de productos
import { ClientesComponent } from './clientes/clientes.component';
import { OrdenesComponent } from './ordenes/ordenes.component';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';

const routes: Routes = [
  { path: 'productos', component: ProductsComponent }, // Ruta para el componente de productos
  { path: 'clientes', component: ClientesComponent  },
  { path: 'ordenes', component: OrdenesComponent    },
  { path: 'login', component: LoginComponent    },
  { path: 'home', component: HomeComponent    }

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
