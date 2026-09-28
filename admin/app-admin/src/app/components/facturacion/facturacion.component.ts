import { Component, OnInit } from '@angular/core';
import { AlegraService } from '../../services/alegra.service';

@Component({
  selector: 'app-facturacion',
  templateUrl: './facturacion.component.html',
  styleUrl: './facturacion.component.css'
})
export class FacturacionComponent implements OnInit {
  resolutions: any[] = [];
  activeResolution: any = null;
  activeError: string | null = null;
  numberTemplates: any[] = [];

  form: any = this.emptyForm();
  editingId: string | null = null;
  showForm = false;

  days = 7;
  pending: any = null;
  sendResult: any = null;
  sending = false;

  message = '';
  messageType: 'success' | 'danger' = 'success';

  constructor(private alegraService: AlegraService) {}

  ngOnInit(): void {
    this.loadResolutions();
    this.loadPending();
    this.alegraService.get_number_templates().subscribe({
      next: (templates) => this.numberTemplates = templates,
      error: () => this.numberTemplates = []
    });
  }

  emptyForm() {
    return {
      alegra_template_id: '',
      prefix: '',
      from_number: 1,
      to_number: null,
      resolution_number: '',
      resolution_date: '',
      valid_until: '',
      active: true
    };
  }

  loadResolutions(): void {
    this.alegraService.get_resolutions().subscribe(data => this.resolutions = data);
    this.alegraService.get_active_resolution().subscribe(data => {
      this.activeResolution = data.resolution;
      this.activeError = data.error;
    });
  }

  newResolution(): void {
    this.form = this.emptyForm();
    this.editingId = null;
    this.showForm = true;
  }

  edit(resolution: any): void {
    this.form = { ...resolution, active: false };
    this.editingId = resolution.id;
    this.showForm = true;
  }

  onTemplateChange(): void {
    const template = this.numberTemplates.find(t => String(t.id) === String(this.form.alegra_template_id));
    if (!template) return;
    this.form.prefix = template.prefix || this.form.prefix;
    this.form.from_number = template.initialNumber || this.form.from_number;
    this.form.to_number = template.finalNumber || this.form.to_number;
    this.form.resolution_number = template.resolution?.number || this.form.resolution_number;
    this.form.resolution_date = template.resolution?.date || this.form.resolution_date;
    this.form.valid_until = template.resolution?.expirationDate || this.form.valid_until;
  }

  save(): void {
    const request = this.editingId
      ? this.alegraService.update_resolution(this.editingId, this.form)
      : this.alegraService.create_resolution(this.form);
    request.subscribe({
      next: () => {
        this.showForm = false;
        this.notify('Resolución guardada', 'success');
        this.loadResolutions();
      },
      error: (err) => this.notify(err.error?.message || 'No se pudo guardar la resolución', 'danger')
    });
  }

  activate(resolution: any): void {
    if (!confirm(`¿Usar la resolución ${resolution.prefix} para las nuevas facturas?`)) return;
    this.alegraService.activate_resolution(resolution.id).subscribe(() => {
      this.notify(`Resolución ${resolution.prefix} activada`, 'success');
      this.loadResolutions();
    });
  }

  remove(resolution: any): void {
    if (!confirm(`¿Eliminar la resolución ${resolution.prefix}?`)) return;
    this.alegraService.delete_resolution(resolution.id).subscribe({
      next: () => this.loadResolutions(),
      error: (err) => this.notify(err.error?.message || 'No se pudo eliminar', 'danger')
    });
  }

  isExpiringSoon(resolution: any): boolean {
    if (!resolution?.valid_until) return false;
    const days = (new Date(resolution.valid_until).getTime() - Date.now()) / 86400000;
    return days < 30 || resolution.remaining < 200;
  }

  loadPending(): void {
    this.alegraService.get_pending_invoices(this.days).subscribe(data => this.pending = data);
  }

  sendPending(): void {
    const total = this.pending?.orders?.length || 0;
    if (!total) return;
    if (!confirm(`Se crearán y emitirán ante la DIAN ${total} facturas con la resolución ${this.activeResolution?.prefix}. ¿Continuar?`)) return;
    this.sending = true;
    this.sendResult = null;
    this.alegraService.send_pending_invoices(this.days).subscribe({
      next: (res) => {
        this.sending = false;
        this.sendResult = res;
        this.notify(`${res.enviadas.length} facturas enviadas, ${res.errores.length} con error`, res.errores.length ? 'danger' : 'success');
        this.loadPending();
        this.loadResolutions();
      },
      error: (err) => {
        this.sending = false;
        this.notify(err.error?.message || 'Error enviando las facturas', 'danger');
      }
    });
  }

  notify(message: string, type: 'success' | 'danger'): void {
    this.message = message;
    this.messageType = type;
  }
}
