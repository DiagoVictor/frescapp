import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './auth.guard';

import { ProductsComponent } from './products/products.component';
import { ClientesComponent } from './clientes/clientes.component';
import { OrdenesComponent } from './ordenes/ordenes.component';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';
import { ReportsComponent } from './reports/reports.component';
import { RestorePasswordComponent } from './restore-password/restore-password.component';
import { DeleteAccountComponent } from './delete-account/delete-account.component';
import { PurchasesComponent } from './purchases/purchases.component';
import { PurchaseComponent } from './purchases/purchase/purchase.component';
import { ListActionnsCustomersComponent } from './crm/list-actionns-customers/list-actionns-customers.component';
import { EditActionComponent } from './crm/edit-action/edit-action.component';
import { NewActionComponent } from './crm/new-action/new-action.component';
import { SuppliersComponent } from './purchases/suppliers/suppliers.component';
import { StopsComponent } from './ruta/stops/stops.component';
import { ListRutasComponent } from './ruta/list-rutas/list-rutas.component';
import { PricingComponent } from './pricing/pricing.component';
import { CostsComponent } from './costs/costs.component';
import { InventoryComponent } from './inventory/inventory.component';
import { EditInventoryComponent } from './inventory/edit-inventory/edit-inventory.component';
import { CierresComponent } from './cierres/cierres/cierres.component';
import { CierreComponent } from './cierres/cierre/cierre.component';
import { ProductsAnalyticsComponent } from './products-analytics/products-analytics.component';
import { CarteraComponent } from './cartera/cartera.component';
import { StrikesComponent } from './strikes/strikes/strikes.component';
import { StrikeComponent } from './strikes/strike/strike.component';
import { UeComponent } from './ue/ue.component';
import { PedidosReportComponent } from './pedidos-report/pedidos-report.component';

const routes: Routes = [
  { path: 'productos', component: ProductsComponent, canActivate: [AuthGuard] },
  { path: 'clientes', component: ClientesComponent, canActivate: [AuthGuard] },
  { path: 'ordenes', component: OrdenesComponent, canActivate: [AuthGuard] },
  { path: 'home', component: HomeComponent, canActivate: [AuthGuard] },
  { path: 'reports', component: ReportsComponent, canActivate: [AuthGuard] },
  { path: 'delete-account', component: DeleteAccountComponent, canActivate: [AuthGuard] },
  { path: 'purchases', component: PurchasesComponent, canActivate: [AuthGuard] },
  { path: 'purchase/:purchaseNumber', component: PurchaseComponent, canActivate: [AuthGuard] },
  { path: 'crm', component: ListActionnsCustomersComponent, canActivate: [AuthGuard] },
  { path: 'edit_action/:action', component: EditActionComponent, canActivate: [AuthGuard] },
  { path: 'newAction', component: NewActionComponent, canActivate: [AuthGuard] },
  { path: 'suppliers', component: SuppliersComponent, canActivate: [AuthGuard] },
  { path: 'rutas', component: ListRutasComponent, canActivate: [AuthGuard] },
  { path: 'precios', component: PricingComponent, canActivate: [AuthGuard] },
  { path: 'costos', component: CostsComponent, canActivate: [AuthGuard] },
  { path: 'inventories', component: InventoryComponent, canActivate: [AuthGuard] },
  { path: 'stops/:route_number', component: StopsComponent, canActivate: [AuthGuard] },
  { path: 'inventory/:id', component: EditInventoryComponent, canActivate: [AuthGuard] },
  { path: 'products-analytics', component: ProductsAnalyticsComponent, canActivate: [AuthGuard] },
  { path: 'cierres', component: CierresComponent, canActivate: [AuthGuard] },
  { path: 'cierre/:fecha', component: CierreComponent, canActivate: [AuthGuard] },
  { path: 'cartera', component: CarteraComponent, canActivate: [AuthGuard] },
  { path: 'strikes', component: StrikesComponent, canActivate: [AuthGuard] },
  { path: 'strike/:id', component: StrikeComponent, canActivate: [AuthGuard] },
  { path: 'ue', component: UeComponent, canActivate: [AuthGuard] },
  { path: 'pedidos-report', component: PedidosReportComponent, canActivate: [AuthGuard] },

  // públicas
  { path: 'login', component: LoginComponent },
  { path: 'restore/:user_id', component: RestorePasswordComponent },

  // por defecto
  { path: '', redirectTo: 'home', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { useHash: false })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
