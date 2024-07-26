import { Component, Input } from '@angular/core';

interface Product {
  total_quantity_ordered: number;
  sku: string;
  name: string;
  price_purchase: number;
  proveedor: string;
  category: string;
  unit: string;
  status: string;
  link_document_support: string;
  final_price_purchase: number;
}

interface Purchase {
  _id: { $oid: string };
  date: string;
  purchase_number: number;
  status: string;
  products: Product[];
}
@Component({
  selector: 'app-purchase',
  standalone: true,
  imports: [],
  templateUrl: './purchase.component.html',
  styleUrl: './purchase.component.css'
})
export class PurchaseComponent {

  selectedProduct: Product | null = null;
  editedPrice: number | null = null;

  constructor() {}

  openEditModal(content: any, product: Product) {
    this.selectedProduct = product;
    this.editedPrice = product.price_purchase;
  }

  savePrice() {
    if (this.selectedProduct && this.editedPrice !== null) {
      this.selectedProduct.price_purchase = this.editedPrice;
      // Aquí puedes añadir una llamada a un servicio para guardar los cambios en el backend
    }
  }
}
