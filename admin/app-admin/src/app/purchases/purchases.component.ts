import { Component } from '@angular/core';
import { PurchaseService } from '../services/purchase.service';
import { Router } from '@angular/router';
import { AlegraService } from '../services/alegra.service';
import { DomSanitizer } from '@angular/platform-browser';
import * as XLSX from 'xlsx';
import * as FileSaver from 'file-saver';
@Component({
  selector: 'app-purchases',
  templateUrl: './purchases.component.html',
  styleUrl: './purchases.component.css'
})
export class PurchasesComponent {
  purchases:  any[]   =[];
  filteredPurchases: any[] = [];
  searchText: string = '';
  fechaNewOrder: string = '';
  messagePurchase = '';
  statusCodePurchase = '';
  pdfData:any;
  constructor(
    private purchaseService: PurchaseService,
    private alegraService: AlegraService,
    private router: Router,
    private sanitizer: DomSanitizer
  ){}
  ngOnInit(): void {
    this.getPurchases();
  }
  navigateToPurchase(purchaseNumber: number) {
    this.router.navigate(['/purchase', purchaseNumber]);
  }
  filterPurchases(){
    if (this.searchText.trim() !== '') {
      this.filteredPurchases = this.purchases.filter(purchase => {
        return purchase.purchase_number.toLowerCase().includes(this.searchText.toLowerCase());
      });
    } else {
      this.filteredPurchases = this.purchases;
    }
  }
  newPurchase() {
    this.purchaseService.createPurchase(this.fechaNewOrder).subscribe(
      (res: any) => {
        this.getPurchases();
        this.messagePurchase = 'Orden de compra creada exitosamente!';
        this.statusCodePurchase = res.statusCode || '200';
        setTimeout(() => {
          this.messagePurchase = '';
        }, 3000);
      },
      (error: any) => {
        this.messagePurchase = 'Fallo al crear la Orden de compra.';
        this.statusCodePurchase = error.status || '500'; 
        setTimeout(() => {
          this.messagePurchase = '';
        }, 3000);
      }
    );
}
  getPurchases(){
    this.purchaseService.getPurchases().subscribe(
      (res: any) => {
        this.purchases = res;
      }
      )
  }
  openPdfModal(purchase_number:any){
    this.pdfData  = this.sanitizer.bypassSecurityTrustResourceUrl(this.purchaseService.getReport(purchase_number));
  }
  delete_purchase(purchase_number:any){
    this.purchaseService.deletePurchase(purchase_number).subscribe(
      (res: any) => {
        this.getPurchases();
        this.messagePurchase = 'Orden de compra eliminada exitosamente!';
        this.statusCodePurchase = res.statusCode || '200';
        setTimeout(() => {
          this.messagePurchase = '';
        }, 3000);
      },
      (error: any) => {
        this.messagePurchase = 'Fallo al eliminar la Orden de compra.';
        this.statusCodePurchase = error.status || '500'; 
        setTimeout(() => {
          this.messagePurchase = '';
        }, 3000);
      }
    );
  }
  calculateRegisteredPercentage(products: any[]): number {
    if (products.length === 0) {
      return 0;
    }
    const registeredCount = products.filter(product => product.status === 'Registrado').length;
    return Math.round((registeredCount / products.length) * 100);
  }
  calculateRegisteredParcialPercentage(products: any[]){
    if (products.length === 0) {
      return 0;
    }
    const registeredCount = products.filter(product => product.status === 'Registro parcial').length;
    return Math.round((registeredCount / products.length) * 100);
  }
  calculateFacturadaPercentage(products: any[]){
    if (products.length === 0) {
      return 0;
    }
    const registeredCount = products.filter(product => product.status === 'Facturada').length;
    return Math.round((registeredCount / products.length) * 100);
  }
  calculateTotalEstimate(products: any[]): number {
    return products.reduce((total, product) => {
      const totalQuantity = Math.max(product.total_quantity || 0, 0); // Asegura que no sea menor a 0
      const productTotal = (product.price_purchase || 0) * totalQuantity;
      return total + productTotal;
    }, 0);
  }
   
  calculatetotalReal(products: any[]): number {
    return products.reduce((total, product) => {
      const productTotal = (product.final_price_purchase || 0) * (product.total_quantity_ordered || 0);
      return total + productTotal;
    }, 0);
  }  
  downloadExcel(purchase: any) {
    const EXCEL_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8';
    const EXCEL_EXTENSION = '.xlsx';
    const worksheetData = purchase.products.map((product: { sku: any; name: any; category: any; price_purchase: number; total_quantity_ordered: number; final_price_purchase:number;  status:any;}) => ({
      SKU: product.sku,
      Nombre: product.name,
      Categoría: product.category,
      Precio_Sugerido: product.price_purchase,
      Precio_Real: product.final_price_purchase,
      Cantidad: product.total_quantity_ordered,
      Total_Sugerido: product.price_purchase * product.total_quantity_ordered,
      Total_Real: product.final_price_purchase * product.total_quantity_ordered,
      status : product.status
    }));
  
    const worksheet = XLSX.utils.json_to_sheet(worksheetData);
    const workbook = { Sheets: { 'Productos': worksheet }, SheetNames: ['Productos'] };
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
  
    // Descargar el archivo Excel
    const data: Blob = new Blob([excelBuffer], { type: EXCEL_TYPE });
    const fileName = `Compra_${purchase.purchase_number}.xlsx`;
    FileSaver.saveAs(data, fileName);
   }
   sync_allegra(purchase: any){
    this.alegraService.send_purchase(purchase.date).subscribe(
      (res: any) => {
        this.getPurchases();
        this.messagePurchase = 'Ordenes de compras sincronizada exitosamente!';
        this.statusCodePurchase = res.statusCode || '200';
        setTimeout(() => {
          this.messagePurchase = '';
        }, 3000);
      },
      (error: any) => {
        this.messagePurchase = 'Fallo al sincronizar las Ordenes de compra.';
        this.statusCodePurchase = error.status || '500'; 
        setTimeout(() => {
          this.messagePurchase = '';
        }, 3000);
      }
    );
    this.getPurchases();
   }
}
