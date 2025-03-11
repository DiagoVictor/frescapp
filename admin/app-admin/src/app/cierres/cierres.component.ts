import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CierresService } from '../services/cierres.service';

@Component({
  selector: 'app-cierres',
  templateUrl: './cierres.component.html',
  styleUrl: './cierres.component.css'
})
export class CierresComponent {
  cierres:any = []
  messageCierres = ''
  fechaNewCierre=''
  statusCodeCierre =''
  currentCierre:any ='';
  constructor(
    private router: Router,
    private cierreService : CierresService
  ){}
  ngOnInit(): void {
    this.getCierres();
  }
  newCierre(){
    this.cierreService.createCierre(this.fechaNewCierre).subscribe(
      (res: any) => {
        this.getCierres();
        this.messageCierres = 'Cierre creado exitosamente!';
        this.statusCodeCierre = res.statusCode || '200';
        setTimeout(() => {
          this.messageCierres = '';
        }, 3000);
      },
      (error: any) => {
        this.messageCierres = 'Fallo al crear el Cierre.';
        this.statusCodeCierre = error.status || '500';
        setTimeout(() => {
          this.messageCierres = '';
        }, 3000);
      }
    );
  }
  delete_inventory(id:any){
    this.cierreService.deleteCierre(id).subscribe(
      (res: any) => {
        this.getCierres();
        this.messageCierres = 'Cierre eliminado exitosamente!';
        this.statusCodeCierre = res.statusCode || '200';
        setTimeout(() => {
          this.messageCierres = '';
        }, 3000);
      },
      (error: any) => {
        this.messageCierres = 'Fallo al eliminar el Cierre.';
        this.statusCodeCierre = error.status || '500';
        setTimeout(() => {
          this.messageCierres = '';
        }, 3000);
      }
    );
  }
  getCierres() {
    this.cierreService.getCierres().subscribe(
      (res: any) => {
        // Ordenar los cierres por close_date de mayor a menor (fecha más reciente primero)
        this.cierres = res.sort((a: any, b: any) => {
          return new Date(b.fecha).getTime() - new Date(a.fecha).getTime();
        });
      }
    );
  }
  editCierre(cierre:any){
      this.currentCierre = cierre;
  }
  saveCierre(){
    this.currentCierre.cierre_total = this.currentCierre.efectivo_total + this.currentCierre.davivienda_total + this.currentCierre.bancolombia_total + this.currentCierre.cartera_total+ this.currentCierre.inventario_hoy - this.currentCierre.deuda_total
    this.cierreService.updateCierre(this.currentCierre).subscribe(
      (res: any) => {
        this.getCierres();
      }
    );
  }
  deleteCierre(){
    this.cierreService.deleteCierre(this.currentCierre.id).subscribe(
      (res: any) => {
        this.getCierres();
      }
    );
  }
}
