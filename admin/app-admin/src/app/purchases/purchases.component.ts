import { Component } from '@angular/core';
import { PurchaseService } from '../services/purchase.service';
import { Router } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';

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
}
