import { Component, OnInit } from '@angular/core';
import { ActionService } from '../../services/action.service';
import { Router } from '@angular/router';
import { ClientesService } from '../../services/clientes.service'; 
import { OrderService } from '../../services/order.service'; 

@Component({
  selector: 'app-new-action',
  templateUrl: './new-action.component.html',
  styleUrls: ['./new-action.component.css'] 
})
export class NewActionComponent implements OnInit {
  newActionObject: any = {
    dateAction: '',
    dateSolution: '',
    type: '',
    customer: { },
    orderNumber: '',
    manager: '',
    status: 'Creada',
    actionComment : '',
    solutionType : '',
    solutionComment:''
  };

  customers: any[] = []; 
  actionTypes: string[] = ['Faltante en Orden', 'Calidad en producto', 'Llegada tarde', 'Recordar realizar pedido', 'Visita presencial', 'Llamada seguimiento']; 
  orders: any[] = []; 
  managers: string[] = ['Wilmer', 'Cata', 'Diago'];
  searchText: string = '';
  constructor(
    private actionService: ActionService,
    private customerService: ClientesService,
    private orderService: OrderService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadCustomers();
  }

  loadCustomers() {
    this.customerService.getClientes().subscribe(
      (data) => {
        this.customers = data;
      },
      (error) => {
        console.error('Error al cargar los clientes:', error);
      }
    );
  }

  loadOrders(customerEmail: string) {
    this.orderService.getLastOrdersByCustomerId(customerEmail).subscribe(
      (data) => {
        this.orders = data;
      },
      (error) => {
        console.error('Error al cargar los pedidos:', error);
      }
    );
  }

  selectCustomer(customer: any) {
    this.newActionObject.customer = customer;
    this.loadOrders(customer.email);
  }

  onTypeChange() {
    if (this.requiresOrderNumber() && this.newActionObject.customer.id) {
      this.loadOrders(this.newActionObject.customer.email);
    }
  }

  requiresOrderNumber(): boolean {
    return this.newActionObject.type === 'Faltante en Orden' || this.newActionObject.type === 'Calidad en producto';
  }

  createAction() {
    if (!this.newActionObject.dateAction || !this.newActionObject.type || !this.newActionObject.customer.id) {
      alert('Por favor, completa todos los campos obligatorios.');
      return;
    }

    this.actionService.createAction(this.newActionObject).subscribe(
      (response) => {
        console.log('Acción creada exitosamente:', response);
        this.router.navigate(['/crm']); // Navegar a la lista de acciones después de crear la acción
      },
      (error) => {
        console.error('Error al crear la acción:', error);
      }
    );
  }
  filteredCustomers(): any[] {
    if (!this.searchText) {
      return this.customers;
    }
    const lowerSearchText = this.searchText.toLowerCase();
    return this.customers.filter(customer => 
      customer.phone.toLowerCase().includes(lowerSearchText) ||
      customer.name.toLowerCase().includes(lowerSearchText) ||
      customer.email.toLowerCase().includes(lowerSearchText)
    );
  }
  backList(){
    this.router.navigate(['/crm'])
  }
}
