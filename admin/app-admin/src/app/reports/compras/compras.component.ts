import { Component } from '@angular/core';
import { OrderService } from '../../services/order.service';

@Component({
  selector: 'app-compras',
  templateUrl: './compras.component.html',
  styleUrls: ['./compras.component.css']
})
export class ComprasComponent {
  fecha: string = '';
  pfdPicking: any = '';
  constructor(private orderService: OrderService){

  }
  generarPDF(): void {
    this.pfdPicking = this.orderService.getCompras(this.fecha);
  }
}
