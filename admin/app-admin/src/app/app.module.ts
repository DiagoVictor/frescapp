import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http'; // Usa HttpClientModule en lugar de provideHttpClient
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NavigationBarComponent } from './navigation-bar/navigation-bar.component';
import { ProductsComponent } from './products/products.component';
import { ClientesComponent } from './clientes/clientes.component';
import { PurchasesComponent } from './purchases/purchases.component';
import { OrdenesComponent } from './ordenes/ordenes.component';
import { PurchaseComponent } from './purchases/purchase/purchase.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';
import { ReportsComponent } from './reports/reports.component';
import { RestorePasswordComponent } from './restore-password/restore-password.component';
import { DeleteAccountComponent } from './delete-account/delete-account.component';
import { ListActionnsCustomersComponent } from './crm/list-actionns-customers/list-actionns-customers.component';
import { NewActionComponent } from './crm/new-action/new-action.component';
import { EditActionComponent } from './crm/edit-action/edit-action.component';
import { NgSelectModule } from '@ng-select/ng-select';
import { CommonModule, DatePipe } from '@angular/common';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { SuppliersComponent  } from './purchases/suppliers/suppliers.component';
import { HashLocationStrategy, LocationStrategy } from '@angular/common';
import { ListRutasComponent  } from './ruta/list-rutas/list-rutas.component';
import { StopsComponent  } from './ruta/stops/stops.component';
import { PricingComponent  } from './pricing/pricing.component';

@NgModule({
  declarations: [
    AppComponent,
    NavigationBarComponent,
    ProductsComponent,
    ClientesComponent,
    OrdenesComponent,
    LoginComponent,
    HomeComponent,
    ReportsComponent,
    RestorePasswordComponent,
    DeleteAccountComponent,
    PurchasesComponent,
    PurchaseComponent,
    ListActionnsCustomersComponent,
    NewActionComponent,
    EditActionComponent,
    SuppliersComponent,
    ListRutasComponent,
    StopsComponent,
    PricingComponent
  ],
  bootstrap: [AppComponent],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    NgSelectModule,
    HttpClientModule,
    ReactiveFormsModule,
    NgbModule
  ],
  providers: [DatePipe,{ provide: LocationStrategy, useClass: HashLocationStrategy }],
})
export class AppModule { }
