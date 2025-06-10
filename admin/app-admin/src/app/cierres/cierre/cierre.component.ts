import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { CierresService } from '../../services/cierres.service';

@Component({
  selector: 'app-cierre',
  templateUrl: './cierre.component.html'
})
export class CierreComponent implements OnInit {
  cierreForm!: FormGroup;
  fechaParam!: string;
  pedidosHoy: any[] = [];
  pedidosManana: any[] = [];
  metricsList = [
    'cost_logistico','cost_warehouse','inventory','orders','lines','gmv',
    'gmv_cash','gmv_davivienda','gmv_bancolombia','gmv_pagado','gmv_cartera',
    'cog','purchases','leakage','aov','alv','margen_neto','utilidad_neta','cost_log_per_orden'
  ];

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    public router: Router,
    private svc: CierresService
  ){}

  ngOnInit() {
    // 1) Leer fecha de la URL
    this.fechaParam = this.route.snapshot.paramMap.get('fecha')!;
    // 2) Cargar datos existentes (si hay) o inicializar vacíos
    this.svc.getCierre(this.fechaParam).subscribe(data => {
      this.pedidosHoy    = data?.pedidosHoy    || [];
      this.pedidosManana = data?.pedidosManana || [];
      this.buildForm(data);
    }, () => this.buildForm());
  }

  private buildForm(data?: any) {
    const hoyGroup = this.metricsList.reduce((acc, key) => {
      acc[key] = [ data?.metricsHoy?.[key] ?? 0, Validators.required ];
      return acc;
    }, {} as any);

    this.cierreForm = this.fb.group({
      fecha:    [ this.fechaParam, Validators.required ],
      ...hoyGroup,
      manana: this.fb.array(
        this.pedidosManana.map((p: any) =>
          this.fb.group({
            numero:       [ p.numero ],
            cliente:      [ p.cliente ],
            total:        [ p.total ],
            conductor:    [ data?.manana?.find((m: any)=>m.numero===p.numero)?.conductor ?? '', Validators.required ],
            fondoCompras: [ data?.manana?.find((m: any)=>m.numero===p.numero)?.fondoCompras ?? 0, Validators.required ]
          })
        )
      )
    });
  }

  get manana(): FormArray {
    return this.cierreForm.get('manana') as FormArray;
  }

  onSubmit() {
    if (this.cierreForm.invalid) return;
    const payload = {
      fecha:      this.cierreForm.value.fecha,
      metricsHoy: this.metricsList.reduce((obj, key) => {
        obj[key] = this.cierreForm.value[key];
        return obj;
      }, {} as any),
      pedidosHoy: this.pedidosHoy,
      pedidosManana: this.cierreForm.value.manana
    };
    this.svc.saveCierre(payload).subscribe(() => {
      this.router.navigate(['/cierres']); // vuelves al listado
    });
  }
}
