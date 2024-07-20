import { Component, OnInit } from '@angular/core';
import { WooService } from '../../services/woo.service';



@Component({
  selector: 'app-integrar',
  templateUrl: './integrar.component.html',
  styleUrls: ['./integrar.component.css']
})
export class IntegrarComponent implements OnInit {
  orderNumber: string = '';
  message: string = '';
  alertClass: string = '';

  constructor(private wooService: WooService) {}
  ngOnInit(): void {
  }

  sendOrder(orderNumber:any) {
    this.wooService.get_order(orderNumber).subscribe((response:any) => {
      if (response) {
        this.message = response.message || 'Order sent successfully';
        this.alertClass = 'alert alert-success';
      } else {
        this.message = response.message || 'Failed to send the order';
        this.alertClass = 'alert alert-danger';
      }
    });
  }
}
