import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http'; // Usa HttpClientModule en lugar de provideHttpClient
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NavigationBarComponent } from './navigation-bar/navigation-bar.component';
import { ProductsComponent } from './products/products.component';
import { ClientesComponent } from './clientes/clientes.component';
import { OrdenesComponent } from './ordenes/ordenes.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';
import { ReportsComponent } from './reports/reports.component';
import { RestorePasswordComponent } from './restore-password/restore-password.component';
import { DeleteAccountComponent } from './delete-account/delete-account.component';
import { PickingComponent } from './reports/picking/picking.component';
import { ComprasComponent } from './reports/compras/compras.component';
import { CotizarComponent  } from './reports/cotizar/cotizar.component';
import { IntegrarComponent } from './reports/integrar/integrar.component';
import { NgSelectModule } from '@ng-select/ng-select';

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
    PickingComponent,
    ComprasComponent,
    CotizarComponent,
    IntegrarComponent
  ],
  bootstrap: [AppComponent],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    NgSelectModule,
    HttpClientModule,
    ReactiveFormsModule
  ],
  providers: []
})
export class AppModule { }
