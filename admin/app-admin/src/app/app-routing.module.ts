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
import { PurchasesComponent } from './purchases/purchases.component';
import { PurchaseComponent } from './purchases/purchase/purchase.component';
import { ListActionnsCustomersComponent } from './crm/list-actionns-customers/list-actionns-customers.component';
import { EditActionComponent } from './crm/edit-action/edit-action.component';
import { NewActionComponent } from './crm/new-action/new-action.component';
import { SuppliersComponent  } from './purchases/suppliers/suppliers.component';
import { StopsComponent  } from './ruta/stops/stops.component';
import { ListRutasComponent  } from './ruta/list-rutas/list-rutas.component';
import { PricingComponent  } from './pricing/pricing.component';
import { CostsComponent  } from './costs/costs.component';
import { InventoryComponent  } from './inventory/inventory.component';
import { EditInventoryComponent  } from './inventory/edit-inventory/edit-inventory.component';
import { ProductsAnalyticsComponent } from './products-analytics/products-analytics.component';
const routes: Routes = [
  { path: 'productos', component: ProductsComponent },
  { path: 'clientes', component: ClientesComponent },
  { path: 'ordenes', component: OrdenesComponent },
  { path: 'login', component: LoginComponent },
  { path: 'home', component: HomeComponent },
  { path: 'reports', component: ReportsComponent },
  { path: 'delete-account', component: DeleteAccountComponent },
  { path: 'restore/:user_id', component: RestorePasswordComponent },
  { path: 'purchases', component: PurchasesComponent },
  { path: 'purchase/:purchaseNumber', component: PurchaseComponent },
  { path: 'crm', component: ListActionnsCustomersComponent },
  { path: 'edit_action/:action', component: EditActionComponent },
  { path: 'newAction', component: NewActionComponent },
  { path: 'suppliers', component: SuppliersComponent },
  { path: 'rutas', component: ListRutasComponent },
  { path: 'precios', component: PricingComponent },
  { path: 'costos', component: CostsComponent },
  { path: 'inventories', component: InventoryComponent },
  { path: 'stops/:route_number', component: StopsComponent },
  { path: 'inventory/:id', component: EditInventoryComponent },
  { path: '', component: HomeComponent },
  { path: 'products-analytics', component: ProductsAnalyticsComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { useHash: false })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
