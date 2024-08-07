import { Component } from '@angular/core';
import { PurchaseService } from '../services/purchase.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-purchases',
  templateUrl: './purchases.component.html',
  styleUrl: './purchases.component.css'
})
export class PurchasesComponent {
  purchases:  any[]   =[];
  filteredPurchases: any[] = [];
  searchText: string = '';
  constructor(
    private purchaseService: PurchaseService,
    private router: Router

  ){}
  ngOnInit(): void {
    this.purchaseService.getPurchases().subscribe(
      (res: any) => {
        this.purchases = res;
      }
      )
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
  newPurchase(){


  }
}
