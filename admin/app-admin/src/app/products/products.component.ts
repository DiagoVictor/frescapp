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
  product: any = {};
  constructor(private productService: ProductService) { }

  ngOnInit(): void {
    this.getProducts();
  }

  getProducts(): void {
    this.productService.getProducts()
      .subscribe(products => this.products = products);
  }
  openEditModal(product: any) {
    this.product = product;
  }
  updated_product(): void {
    this.productService.updateProduct(this.product.id, this.product).subscribe((data: any) => {
    });
  }
  created_product(): void {

  }
  updatePrice(): void{

  }
}
