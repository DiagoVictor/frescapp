import { Component, ElementRef, OnInit } from '@angular/core';
import { OrderService } from '../services/order.service';
import { Router } from '@angular/router';
import { ProductService } from '../services/product.service';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';


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
  documentTypes: string[] = [];
  paymentMethods: string[] = [];
  deliverySlots: string[] = [];
  orderStatus: string[] = ['Creada', 'Confirmada', 'Despachada', 'Entregada', 'Facturada', 'Archivada'];
  productos: any[] = [];
  selectedsku: string = '';
  pdfData: any;
  constructor(private orderService: OrderService, private router: Router,
    private productService: ProductService, private sanitizer: DomSanitizer) { }

  ngOnInit(): void {
    const isLoggedIn = this.checkIfLoggedIn();

    if (!isLoggedIn) {
      this.router.navigate(['/login']);
    } else {
      this.getOrders();
      this.orderService.getConfig().subscribe(config => {
        this.documentTypes = config.document_type;
        this.paymentMethods = config.payments_method;
        this.deliverySlots = config.delivery_slots;
      });
      this.obtenerProductos();

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
        return ['order_number', 'customer_email', 'customer_phone', 'customer_documentNumber', 'customer_name', 'delivery_date', 'status']
          .some(key => order[key]?.toLowerCase().includes(this.searchText.toLowerCase()));
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
    const currentDate: Date = new Date();
    // Obtener los componentes de la fecha y hora
    const year: number = currentDate.getFullYear();
    const month: number = currentDate.getMonth() + 1; // Los meses comienzan desde 0
    const day: number = currentDate.getDate();
    const hours: number = currentDate.getHours();
    const minutes: number = currentDate.getMinutes();
    const seconds: number = currentDate.getSeconds();

    // Formatear la fecha y hora
    const formattedDate: string = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')} ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

    this.order.total = parseFloat(this.order.total);
    this.order.updated_at = formattedDate;
    this.orderService.updateOrder(this.order.id, this.order).subscribe((data: any) => {
      // Lógica después de actualizar la orden, si es necesario
    });

    this.getOrders();
  }
  created_order(): void {
    const currentDate: Date = new Date();
    // Obtener los componentes de la fecha y hora
    const year: number = currentDate.getFullYear();
    const month: number = currentDate.getMonth() + 1; // Los meses comienzan desde 0
    const day: number = currentDate.getDate();
    const hours: number = currentDate.getHours();
    const minutes: number = currentDate.getMinutes();
    const seconds: number = currentDate.getSeconds();

    // Formatear la fecha y hora
    const formattedDate: string = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')} ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

    this.order.created_at = formattedDate;
    this.order.updated_at = formattedDate;
    this.order.total = parseFloat(this.order.total);
    this.orderService.createOrder(this.order).subscribe((data: any) => {
      // Lógica después de crear una nueva orden, si es necesario
    });
    this.getOrders();
  }
  saveOrder() {
    if (this.actionType === 'update') {
      this.updated_order();
    } else if (this.actionType === 'new') {
      this.created_order();
    }
  }
  camposCompletos(): boolean {
    const { order_number, customer_email, customer_phone, customer_documentNumber, customer_documentType, customer_name, delivery_date, status } = this.order;
    return !!order_number && !!customer_email && !!customer_phone && !!customer_documentNumber && !!customer_documentType && !!customer_name && !!delivery_date && !!status;
  }
  removeProduct(product: any): void {
    const index = this.order.products.indexOf(product);
    if (index !== -1) {
      this.order.products.splice(index, 1);
    }
  }
  addProduct(): void {
    if (!this.order.products) {
      this.order.products = [];
    }
    this.order.products.push({
      sku: '',
      name: '',
      price_sale: 0,
      quantity: 1,
      iva: false,
      iva_value: 0
    });
  }
  obtenerProductos(): void {
    this.productService.getProducts()
      .subscribe(
        (data: any) => {
          this.productos = data;
        },
      );
  }
  openPdfModal(order: any): void {
    this.pdfData = this.sanitizer.bypassSecurityTrustResourceUrl('app.buyfrescapp.com/api/order/generate_pdf/' + order);

  }

}
