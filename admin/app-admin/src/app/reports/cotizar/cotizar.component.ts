import { Component } from '@angular/core';
import { ProductService } from '../../services/product.service';

@Component({
  selector: 'app-cotizar',
  templateUrl: './cotizar.component.html',
  styleUrls: ['./cotizar.component.css']
})
export class CotizarComponent {
  fecha: string = '';
  products: any[] = [];
  price: number = 0;
  searchTerm : string = '';
  constructor(private productService: ProductService) { }
  ngOnInit(): void {
      this.getProducts();
  }
  getProducts(): void {
    this.productService.getProducts()
      .subscribe(products => {
        this.products = products;
      });
  }
  cotizarProducto(){

  }
  filterProducts(){

  }
}
