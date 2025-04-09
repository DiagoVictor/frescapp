import { Component,  OnInit } from '@angular/core';
import { OrderService } from '../services/order.service';

@Component({
  selector: 'app-cartera',
  templateUrl: './cartera.component.html',
  styleUrl: './cartera.component.css'
})
export class CarteraComponent implements OnInit {
  constructor(
    private orderService: OrderService
  ) { }
  orders:any = [];
  total_cartera = 0;
  searchText:String ='';
  ordersFiltered: any = [];
  ngOnInit(): void {
    this.orderService.getOrdersByStatus("Pendiente de pago")
    .subscribe(orders => {
      this.orders = orders;
      this.ordersFiltered = orders; // Inicializa ordersFiltered con todos los pedidos
      this.total_cartera = this.ordersFiltered.reduce((sum: number, order: any) => {
        // Asegúrate de que order.total es un número y no es null/undefined
        const orderTotal = order.total - order.totalPayment  ? Number(order.total - order.totalPayment ) : 0;
        return sum + orderTotal;
      }, 0);
      this.total_cartera = parseFloat(this.total_cartera.toFixed(2));
    });

  }
  filterorders(){
    if (this.searchText.trim() !== '') {
      const searchTextLower = this.searchText.toLowerCase();
      this.ordersFiltered = this.orders.filter((order: { cliente: any; delivery_date: any; order_number: any; customer_email: any; customer_phone: { toString: () => any; }; deliveryAddress: { toString: () => any; }; status: { toString: () => any; }; paymentMethod: { toString: () => any; }; driver_name: { toString: () => any; }; }) => {
        return (
          (order.cliente ?? '').toLowerCase().includes(searchTextLower) ||
          (order.delivery_date ?? '').toLowerCase().includes(searchTextLower) ||
          (order.order_number ?? '').toLowerCase().includes(searchTextLower) ||
          (order.customer_email ?? '').toLowerCase().includes(searchTextLower) ||
          (order.customer_phone?.toString() ?? '').includes(searchTextLower) ||
          (order.deliveryAddress?.toString() ?? '').includes(searchTextLower) ||
          (order.status?.toString() ?? '').includes(searchTextLower) ||
          (order.paymentMethod?.toString() ?? '').includes(searchTextLower) ||
          (order.driver_name?.toString() ?? '').includes(searchTextLower)
        );
      });
    } else {
      this.ordersFiltered = this.orders;
    }
    this.total_cartera = this.ordersFiltered.reduce((sum: number, order: any) => {
      // Asegúrate de que order.total es un número y no es null/undefined
      const orderTotal = order.total - order.totalPayment  ? Number(order.total - order.totalPayment ) : 0;
      return sum + orderTotal;
    }, 0);
    this.total_cartera = parseFloat(this.total_cartera.toFixed(2));
  }
  daysMora(order: any): number {
    if (!order.delivery_date) {
      return 0;
    }
    const deliveryDate = new Date(order.delivery_date);
    const today = new Date();
    // Calcula la diferencia en milisegundos
    const diffMs = today.getTime() - deliveryDate.getTime();
    // Convierte la diferencia a días
    return Math.floor(diffMs / (1000 * 3600 * 24));
  }
}

