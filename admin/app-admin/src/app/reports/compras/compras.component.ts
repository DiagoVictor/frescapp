import { Component } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-compras',
  templateUrl: './compras.component.html',
  styleUrls: ['./compras.component.css']
})
export class ComprasComponent {
  fecha: string = '';
  pdfPicking: any = '';
  supplier  :any = 'Todos';
  constructor(private sanitizer: DomSanitizer) {}
  generarPDF(): void {
    this.pdfPicking = this.sanitizer.bypassSecurityTrustResourceUrl('https://app.buyfrescapp.com:5000/api/reports/compras/' + this.fecha + "/" + this.supplier ) ;
  }
}
