import { Component, OnInit } from '@angular/core';
import { ProductService } from '../product.service';
import { NgModule } from '@angular/core';

@Component({
  selector: 'app-products',
  templateUrl: './products.component.html',
  styleUrls: ['./products.component.css']
})
export class ProductsComponent implements OnInit {
  products: any[] | undefined;
  product: any = { };
  actionTipo: any = '';
  constructor(private productService: ProductService) { }

  ngOnInit(): void {
    this.getProducts();
  }

  getProducts(): void {
    this.productService.getProducts()
      .subscribe(products => this.products = products);
  }
  openEditModal(product: any,tipo:any) {
    this.product = product;
    this.actionTipo = tipo
  }
  updated_product(): void {
    this.productService.updateProduct(this.product.id, this.product).subscribe((data: any) => {
    });
    this.getProducts();
  }
  created_product() {
    this.productService.createProduct(this.product).subscribe((data: any) => {
    });
    this.getProducts();
  }
  updatePrice(): void{

  }
  camposCompletos(): boolean {
    const { name, unit, category, sku, price_sale, price_purchase, discount, margen, iva, iva_value, description, image, status } = this.product;
    return !!name && !!unit && !!category && !!sku && !!price_sale && !!price_purchase && !!discount && !!margen && !!iva && !!iva_value && !!description && !!image && !!status;
  }

}
