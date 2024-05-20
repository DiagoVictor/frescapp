import { Component } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-picking',
  templateUrl: './picking.component.html',
  styleUrls: ['./picking.component.css']
})

export class PickingComponent {
  fecha: string = '';
  pdfPicking: any = '';
  constructor(private sanitizer: DomSanitizer) {}


  generarPDF(): void {
    this.pdfPicking = this.sanitizer.bypassSecurityTrustResourceUrl('http://app.buyfrescapp.com:5000/api/reports/picking/' + this.fecha);
  }
}
