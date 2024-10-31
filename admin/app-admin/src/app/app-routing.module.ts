import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ProductsComponent } from './products/products.component';
import { ClientesComponent } from './clientes/clientes.component';
import { OrdenesComponent } from './ordenes/ordenes.component';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';
import { ReportsComponent } from './reports/reports.component';
import { RestorePasswordComponent } from './restore-password/restore-password.component';
import { DeleteAccountComponent } from './delete-account/delete-account.component';
import { PickingComponent } from './reports/picking/picking.component';
import { ComprasComponent } from './reports/compras/compras.component';
import { CotizarComponent } from './reports/cotizar/cotizar.component';
import { IntegrarComponent } from './reports/integrar/integrar.component';
import { PurchasesComponent } from './purchases/purchases.component';
import { PurchaseComponent } from './purchases/purchase/purchase.component';
import { ListActionnsCustomersComponent } from './crm/list-actionns-customers/list-actionns-customers.component';
import { EditActionComponent } from './crm/edit-action/edit-action.component';
import { NewActionComponent } from './crm/new-action/new-action.component';
import { SuppliersComponent  } from './suppliers/suppliers.component';
import { StopsComponent  } from './ruta/stops/stops.component';
import { ListRutasComponent  } from './ruta/list-rutas/list-rutas.component';

const routes: Routes = [
  { path: 'productos', component: ProductsComponent },
  { path: 'clientes', component: ClientesComponent },
  { path: 'ordenes', component: OrdenesComponent },
  { path: 'login', component: LoginComponent },
  { path: 'home', component: HomeComponent },
  { path: 'reports', component: ReportsComponent },
  { path: 'reports/picking', component: PickingComponent },
  { path: 'reports/compras', component: ComprasComponent },
  { path: 'reports/cotizar', component: CotizarComponent },
  { path: 'reports/integrar', component: IntegrarComponent },
  { path: 'delete-account', component: DeleteAccountComponent },
  { path: 'restore/:user_id', component: RestorePasswordComponent },
  { path: 'purchases', component: PurchasesComponent },
  { path: 'purchase/:purchaseNumber', component: PurchaseComponent },
  { path: 'crm', component: ListActionnsCustomersComponent },
  { path: 'edit_action/:action', component: EditActionComponent },
  { path: 'newAction', component: NewActionComponent },
  { path: 'suppliers', component: SuppliersComponent },
  { path: 'rutas', component: ListRutasComponent },
  { path: 'stops/:route_number', component: StopsComponent },
  { path: '', component: HomeComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { useHash: false })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
