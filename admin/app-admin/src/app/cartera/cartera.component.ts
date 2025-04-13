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
  total_orders = 0;
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
      this.total_orders = this.orders.length;
    });

  }
  filterorders() {
    const searchTextLower = this.searchText.trim().toLowerCase();

    if (searchTextLower !== '') {
      this.ordersFiltered = this.orders.filter((order: any) => {
        const fieldsToSearch = [
          order.cliente,
          order.delivery_date,
          order.customer_name,
          order.order_number,
          order.customer_email,
          order.customer_phone,
          order.deliveryAddress,
          order.status,
          order.paymentMethod,
          order.driver_name
        ];

        return fieldsToSearch.some(field =>
          (field ?? '').toString().toLowerCase().includes(searchTextLower)
        );
      });
    } else {
      this.ordersFiltered = this.orders;
    }

    this.total_cartera = this.ordersFiltered.reduce((sum: number, order: any) => {
      const total = Number(order.total ?? 0);
      const payment = Number(order.totalPayment ?? 0);
      return sum + (total - payment);
    }, 0);

    this.total_cartera = parseFloat(this.total_cartera.toFixed(2));
    this.total_orders = this.ordersFiltered.length;
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

