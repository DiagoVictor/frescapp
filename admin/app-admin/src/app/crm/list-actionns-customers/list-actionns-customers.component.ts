import { Component } from '@angular/core';
import { ActionService } from '../../services/action.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-list-actionns-customers',
  templateUrl: './list-actionns-customers.component.html',
  styleUrl: './list-actionns-customers.component.css'
})
export class ListActionnsCustomersComponent {
  actions:  any[]   =[];
  filteredActions: any[] = [];
  searchText: string = '';
  messageAction: string ='';
  statusCodeAction : string = '' ;
  actionSelect :any;
  constructor(
    private actionService: ActionService,
    private router: Router  ){}
  ngOnInit(): void {
    this.getActions();
  }
  navigateToaAction(actionNumber: number) {
    this.router.navigate(['/action', actionNumber]);
  }
  filterActions(){
    if (this.searchText.trim() !== '') {
      this.filteredActions = this.actions.filter(action => {
        return action.purchase_number.toLowerCase().includes(this.searchText.toLowerCase());
      });
    } else {
      this.filteredActions = this.actions;
    }
  }
  newAction() {
    this.router.navigate(['/newAction']);
}
  getActions(){
    this.actionService.getActions().subscribe(
      (res: any) => {
        this.actions = res;
      }
      )
  }

  delete_action(actionNumnber:any){
    this.actionService.deleteAction(actionNumnber).subscribe(
      (res: any) => {
        this.getActions();
        this.messageAction = 'Accion eliminada exitosamente!';
        this.statusCodeAction = res.statusCode || '200';
        setTimeout(() => {
          this.messageAction = '';
        }, 3000);
      },
      (error: any) => {
        this.messageAction = 'Fallo al eliminar la accion.';
        this.statusCodeAction = error.status || '500'; 
        setTimeout(() => {
          this.messageAction = '';
        }, 3000);
      }
    );
  }
  resolver(actionNumnber:any){
    this.router.navigate(['/edit_action',actionNumnber]);
  }
  viewAction(action:any){
    this.actionSelect = action;
  }
}

