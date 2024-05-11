import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http'; // Importa HttpClientModule
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NavigationBarComponent } from './navigation-bar/navigation-bar.component';
import { ProductsComponent } from './products/products.component';
import { ClientesComponent } from './clientes/clientes.component';
import { OrdenesComponent } from './ordenes/ordenes.component';
import { FormsModule } from '@angular/forms';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';
import { ReportsComponent } from './reports/reports.component';
import { RestorePasswordComponent } from './restore-password/restore-password.component';
import { DeleteAccountComponent } from './delete-account/delete-account.component'; // Importa FormsModule


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
    DeleteAccountComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
