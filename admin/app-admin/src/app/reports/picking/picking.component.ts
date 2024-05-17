import { Component } from '@angular/core';
import { OrderService } from '../../services/order.service';

@Component({
  selector: 'app-picking',
  templateUrl: './picking.component.html',
  styleUrls: ['./picking.component.css']
})
export class PickingComponent {
  fecha: string = '';
  pfdPicking: any = '';
  constructor(private orderService: OrderService){

  }
  generarPDF(): void {
    this.pfdPicking = this.orderService.getPicking(this.fecha);
  }
}
