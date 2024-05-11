import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ProductsComponent } from './products/products.component'; // Importa el componente de productos
import { ClientesComponent } from './clientes/clientes.component';
import { OrdenesComponent } from './ordenes/ordenes.component';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';
import { ReportsComponent } from './reports/reports.component';
import { RestorePasswordComponent } from './restore-password/restore-password.component';
import { DeleteAccountComponent } from './delete-account/delete-account.component';
const routes: Routes = [
  { path: 'productos', component: ProductsComponent }, // Ruta para el componente de productos
  { path: 'clientes', component: ClientesComponent  },
  { path: 'ordenes', component: OrdenesComponent    },
  { path: 'login', component: LoginComponent    },
  { path: 'home', component: HomeComponent    },
  { path: 'reports', component: ReportsComponent    },
  { path: 'delete-account', component: DeleteAccountComponent    },
  { path: 'restore/:user_id', component: RestorePasswordComponent    },
  { path: '', component: HomeComponent    }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { useHash: false })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
