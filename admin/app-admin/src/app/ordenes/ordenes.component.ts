import { Component, OnInit } from '@angular/core';
import { OrderService } from '../order.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-orders',
  templateUrl: './ordenes.component.html',
  styleUrls: ['./ordenes.component.css']
})
export class OrdenesComponent implements OnInit {
  orders: any[] | [] | undefined;
  filteredOrders: any[] | undefined;
  searchText: string = '';
  order: any = {};
  actionType: any = '';
  successMessage: string = '';

  constructor(private orderService: OrderService, private router: Router) { }

  ngOnInit(): void {
    const isLoggedIn = this.checkIfLoggedIn();

    if (!isLoggedIn) {
      this.router.navigate(['/login']);
    } else {
      this.getOrders();
    }
  }

  checkIfLoggedIn(): boolean {
    const token = localStorage.getItem('token');
    return !!token;
  }

  getOrders(): void {
    this.orders = [];
    this.filteredOrders = [];
    this.orderService.getOrders()
      .subscribe(orders => {
        this.orders = orders;
        this.filteredOrders = orders;
        this.filterOrders();
      });
  }

  filterOrders(): void {
    if (this.searchText.trim() !== '') {
      this.filteredOrders = this.orders?.filter(order => {
        return order.order_number.toLowerCase().includes(this.searchText.toLowerCase());
      });
    } else {
      this.filteredOrders = this.orders;
    }
  }

  openEditModal(order: any, type: any): void {
    this.order = order;
    this.actionType = type;
  }

  updated_order(): void {
    this.orderService.updateOrder(this.order.id, this.order).subscribe((data: any) => {
      // Lógica después de actualizar la orden, si es necesario
    });

    this.getOrders();
  }

  created_order(): void {
    this.orderService.createOrder(this.order).subscribe((data: any) => {
      // Lógica después de crear una nueva orden, si es necesario
    });

    this.getOrders();
  }

  camposCompletos(): boolean {
    const { order_number, customer_email, customer_phone, customer_documentNumber, customer_documentType, customer_name, delivery_date, status } = this.order;
    return !!order_number && !!customer_email && !!customer_phone && !!customer_documentNumber && !!customer_documentType && !!customer_name && !!delivery_date && !!status;
  }
    // Función para eliminar un producto de la orden
    removeProduct(product: any): void {
      const index = this.order.products.indexOf(product);
      if (index !== -1) {
        this.order.products.splice(index, 1);
      }
    }
    addProduct(): void {

      this.order.products.push({
            sku: '',
            name: '',
            price_sale : 0,
            quantity: 1,
            iva: false,
            iva_value: 0
          });
        }


}
