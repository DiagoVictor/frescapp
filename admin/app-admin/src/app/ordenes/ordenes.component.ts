import { Component,  OnInit } from '@angular/core';
import { OrderService } from '../services/order.service';
import { Router } from '@angular/router';
import { ProductService } from '../services/product.service';
import { ClientesService } from '../services/clientes.service';
import { DomSanitizer } from '@angular/platform-browser';
import { AlegraService } from '../services/alegra.service';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-orders',
  templateUrl: './ordenes.component.html',
  styleUrls: ['./ordenes.component.css']
})
export class OrdenesComponent implements OnInit {
  orders: any[] | [] | undefined;
  filteredOrders: any[] | undefined;
  searchText: string = '';
  searchDate: string | undefined;
  order: any = {};
  product: any = {};
  customers: any[]  = [];
  selectedCustomerId: number | undefined;
  actionType: any = '';
  successMessage: string = '';
  failedMessage: any = '';
  documentTypes: string[] = [];
  paymentMethods: string[] = [];
  deliverySlots: string[] = [];
  orderStatus: string[] = ['Creada', 'Confirmada', 'Despachada', 'Entregada', 'Facturada', 'Archivada'];
  products: any[] = [];
  selectedProductId: number | undefined;
  selectedsku: string = '';
  pdfData: any;
  facturaData: any;
  messageAlegra = '';
  statusCodeAlegra = '';
  sortColumn: string = '';
  sortDirection: string = 'asc';
  constructor(
    private orderService: OrderService
    ,private router: Router
    ,private productService: ProductService
    ,private clienteService: ClientesService
    ,private sanitizer: DomSanitizer
    ,private alegraService: AlegraService
    ,private datePipe: DatePipe
  ) { }

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
      this.getCustomers();

    }
  }
  checkIfLoggedIn(): boolean {
    const token = localStorage.getItem('token');
    return !!token;
  }
  getOrders(): void {
    this.orders = [];
    this.orderService.getOrders(this.datePipe.transform(this.searchDate, 'yyyy-MM-dd') || 'all')
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
      this.getOrders()
    } else if (this.actionType === 'new') {
      this.created_order();
      this.getOrders()
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
          this.products = data;
        },
      );
  }
  openPdfModal(order: any): void {
    this.pdfData = this.sanitizer.bypassSecurityTrustResourceUrl('https://app.buyfrescapp.com:5000/api/order/generate_pdf/' + order);
  }
  getCustomers(){
    this.clienteService.getClientes()
      .subscribe(customers => {
        this.customers = customers;
      });
  }
  filteredCustomers() {
    if (!this.searchText) {
      return this.customers;
    }
    return this.customers.filter(customer =>
      customer.name.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }
  onCustomerSelect() {
    const selectedCustomer = this.customers.find(customer => customer.id === this.selectedCustomerId);
    if (selectedCustomer) {
      this.order.customer_name = selectedCustomer.name;
      this.order.customer_email = selectedCustomer.email;
      this.order.customer_phone = selectedCustomer.phone;
      this.order.customer_documentNumber = selectedCustomer.document;
      this.order.customer_documentType = selectedCustomer.document_type;
      this.order.deliveryAddress = selectedCustomer.address;
    }
  }
  onProductSelect(product: { id: any; name: any; sku: any; price_sale: any; iva: any; iva_value: any; }): void {
    const selectedProduct = this.products.find(p => p.id === product.id);
    if (selectedProduct) {
      product.name = selectedProduct.name;
      product.sku = selectedProduct.sku;
      product.price_sale = selectedProduct.price_sale;
      product.iva = selectedProduct.iva;
      product.iva_value = selectedProduct.iva_value;
    }
  }
  sync_allegra(order_number: any) {
    this.alegraService.send_invoice(order_number).subscribe(
      (res: any) => {
          if (res.status == '201'){
          this.statusCodeAlegra = '201';
          this.messageAlegra = res.message || 'Factura creada exitosamente.'; // Ajusta este mensaje según lo que devuelva la API
        }else{
          this.statusCodeAlegra == '400';
          this.messageAlegra = res.error?.message || 'Ocurrió un error'; // Ajusta el mensaje de error según sea necesario
        }
        this.getOrders()
      },
      (error) => {
        this.statusCodeAlegra = error.status.toString(); // Obtiene el código de estado del error
        this.messageAlegra = error.error?.message || 'Ocurrió un error'; // Ajusta el mensaje de error según sea necesario
        this.getOrders()
      }
    );
  }
  get_invoice(id: any){
    this.alegraService.get_invoice('215').subscribe(
      (res: any) => {
        console.log(res.text)

      }
    );
    //this.facturaData =
  }
  delete_order(id: any){
    this.orderService.deleteOrder(id).subscribe(
      (res: any) => {
        this.getOrders()
      }
    );
  }
  sort(column: string) {
    console.log(column)
    if (!this.filteredOrders || this.filteredOrders.length === 0) {
      return; // No hacer nada si filteredOrders es indefinido o está vacío
    }

    if (this.sortColumn === column) {
      // Si ya está ordenado por esta columna, invertir la dirección
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      // Si se selecciona una nueva columna, ordenar por ella en orden ascendente
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }

    // Ordenar filteredOrders según la columna y dirección
    this.filteredOrders.sort((a, b) => {
      const valueA = a[this.sortColumn];
      const valueB = b[this.sortColumn];

      if (valueA == null) return this.sortDirection === 'asc' ? 1 : -1;
      if (valueB == null) return this.sortDirection === 'asc' ? -1 : 1;

      if (valueA < valueB) return this.sortDirection === 'asc' ? -1 : 1;
      if (valueA > valueB) return this.sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }
}

