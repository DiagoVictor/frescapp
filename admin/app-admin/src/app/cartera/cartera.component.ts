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
  ngOnInit(): void {
    this.orderService.getOrdersByStatus("Pendiente de pago")
    .subscribe(orders => {
      this.orders = orders;
      this.total_cartera = this.orders.reduce((sum: number, order: any) => {
        // Asegúrate de que order.total es un número y no es null/undefined
        const orderTotal = order.total ? Number(order.total) : 0;
        return sum + orderTotal;
      }, 0);

      // Opcional: Redondear a 2 decimales si es necesario
      this.total_cartera = parseFloat(this.total_cartera.toFixed(2));
    });

  }
}
