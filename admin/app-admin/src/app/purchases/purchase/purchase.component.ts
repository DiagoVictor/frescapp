import { Component, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { PurchaseService } from '../../services/purchase.service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { SupplierService } from '../../services/supplier.service';

@Component({
  selector: 'app-purchase',
  templateUrl: './purchase.component.html',
  styleUrls: ['./purchase.component.css']
})
export class PurchaseComponent {

  selectedProduct: any | null = null;
  editedPrice: number | null = null;
  purchaseNumber = '';
  purchase: any | null = null;
  filteredProducts: any[] = [];
  searchTerm: string = '';
  sortColumn: string = '';
  sortDirection: number = 1; // 1 for ascending, -1 for descending
  successMessage: string | null = null;
  errorMessage: string | null = null;
  suppliers: any[] = [];
  constructor(
    private route: ActivatedRoute,
    private purchaseService: PurchaseService,
    private modalService: NgbModal,
    private supplierService : SupplierService
  ) {
    this.route.params.subscribe(params => {
      this.purchaseNumber = params['purchaseNumber'];
    });
  }

  ngOnInit(): void {
    this.purchaseService.getPurchase(this.purchaseNumber).subscribe(
      (res: any) => {
        this.purchase = res;        
        this.filteredProducts = this.purchase.products.sort((a: any, b: any) => {
          if (a.category.toLowerCase() < b.category.toLowerCase()) {
            return -1;
          } else if (a.category.toLowerCase() > b.category.toLowerCase()) {
            return 1;
          } else {
            return 0;
          }
        });
      }
    );
    this.supplierService.getSuppliers().subscribe(
      (res: any) => {
        this.suppliers = res;
      }
    );
  }

  filterProducts() {
    this.filteredProducts = this.purchase.products.filter((product: any) =>
      product.name.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }

  sortBy(column: string) {
    if (this.sortColumn === column) {
      this.sortDirection = -this.sortDirection;
    } else {
      this.sortColumn = column;
      this.sortDirection = 1;
    }
    this.filteredProducts.sort((a: any, b: any) => {
      if (a[column] < b[column]) {
        return -1 * this.sortDirection;
      }
      if (a[column] > b[column]) {
        return 1 * this.sortDirection;
      }
      return 0;
    });
  }

  openEditModal(content: any, product: any) {
    this.selectedProduct = product;
    this.editedPrice = 0;
    this.modalService.open(content);
    this.successMessage = null;
    this.errorMessage = null;
    if (this.selectedProduct.proveedor) {
      // Buscar el objeto completo del proveedor en la lista de suppliers
      this.selectedProduct.proveedor = this.suppliers.find(
        supplier => supplier.id === this.selectedProduct.proveedor.id
      );
    }
  }

  savePrice() {
    let status = 'Creada';
    if (this.selectedProduct.final_price_purchase > 0 && this.selectedProduct.proveedor) {
      status = 'Registrado';
    } else if (this.selectedProduct.final_price_purchase || this.selectedProduct.proveedor) {
      status = 'Registro parcial';
    }
    this.selectedProduct.status = status;
    const data = {
      sku: this.selectedProduct.sku,
      purchase_number: this.purchaseNumber,
      final_price_purchase: this.selectedProduct.final_price_purchase,
      proveedor: this.selectedProduct.proveedor,
      status: status 
    };
  
    this.purchaseService.updatePrice(data).subscribe(
      (res: any) => {
        this.successMessage = 'Precio guardado exitosamente.';
        this.errorMessage = null;
      },
      (error: any) => {
        this.successMessage = null;
        this.errorMessage = 'Error al guardar el precio.';
      }
    );
  }
  
}
