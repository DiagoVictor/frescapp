import { Component, OnInit } from '@angular/core';
import { ClientesService } from '../services/clientes.service';

@Component({
  selector: 'app-clientes',
  templateUrl: './clientes.component.html',
  styleUrls: ['./clientes.component.css']
})
export class ClientesComponent implements OnInit {
  customers: any[] = [];
  filteredCustomers: any[] = [];
  searchText: string = '';
  selectedCustomer: any = {};
  isNewCustomer: boolean = true;

  constructor(private clientesService: ClientesService) {}

  ngOnInit(): void {
    this.getClientes();
  }

  getClientes() {
    this.clientesService.getClientes().subscribe(
      (data) => {
        this.customers = data;
        this.filteredCustomers = this.customers;
      },
      (error) => {
        console.error('Error al obtener clientes:', error);
        // Manejo de errores
      }
    );
  }

  filterCustomers() {
    this.filteredCustomers = this.customers.filter(customer =>
      customer.name.toLowerCase().includes(this.searchText.toLowerCase()) ||
      customer.phone.toLowerCase().includes(this.searchText.toLowerCase()) ||
      customer.document.toLowerCase().includes(this.searchText.toLowerCase()) ||
      customer.email.toLowerCase().includes(this.searchText.toLowerCase()) ||
      customer.restaurant_name.toLowerCase().includes(this.searchText.toLowerCase()) ||
      customer.status.toLowerCase().includes(this.searchText.toLowerCase()) ||
      customer.category.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }

  openEditModal(customer: any, type: string): void {
    this.isNewCustomer = type === 'new';
    this.selectedCustomer = type === 'new' ? {} : { ...customer };
  }

  edit_customer(customer: any) {
    this.openEditModal(customer, 'edit');
  }

  saveCustomer() {

  }


  delete_customer(customer: any) {
    if (confirm('¿Está seguro de que desea eliminar este cliente?')) {
      this.clientesService.deleteCliente(customer._id).subscribe(
        () => {
          this.customers = this.customers.filter(c => c._id !== customer._id);
          this.filterCustomers();
        },
        (error) => {
          console.error('Error al eliminar cliente:', error);
          // Manejo de errores
        }
      );
    }
  }
}
