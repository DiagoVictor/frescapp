import { Component, OnInit } from '@angular/core';
import { ActionService } from '../../services/action.service';
import { Router, ActivatedRoute } from '@angular/router';
import { ClientesService } from '../../services/clientes.service'; 
import { OrderService } from '../../services/order.service'; 
import { timestamp } from 'rxjs';
@Component({
  selector: 'app-edit-action',
  templateUrl: './edit-action.component.html',
  styleUrl: './edit-action.component.css'
})
export class EditActionComponent {
  actionObject: any = {
    dateAction: '',
    dateSolution: '',
    type: '',
    customer: { },
    orderNumber: '',
    manager: '',
    status: '',
    actionComment : '',
    solutionType : '',
    solutionComment:''
  };

  solutions :string[]  = ['Llamada', 'Visita','Whatsapp']
  constructor(
    private actionService: ActionService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.loadAction();
  }

  loadAction() {
    const actionId = this.route.snapshot.paramMap.get('action');
    if (actionId) {
      this.actionService.getAction(actionId).subscribe(
        (data) => {
          this.actionObject = data;
        },
        (error) => {
          console.error('Error al cargar la acción:', error);
        }
      );
    }
  }

  backList(){
    this.router.navigate(['/crm'])
  }
  completar(){
    this.actionObject.dateSolution = new Date().toISOString();
    this.actionObject.status = 'Completada';
    this.actionService.editAction(this.actionObject.actionNumber ,this.actionObject).subscribe((res)=>{
      this.router.navigate(['/crm']);
    }
    );
  }
}