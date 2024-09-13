import { Component } from '@angular/core';
import { ActionService } from '../../services/action.service';
import { Router } from '@angular/router';
import { DatePipe } from '@angular/common';

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
  managers: string[] = ['Ferney', 'Cata', 'Diago','Saco'];
  searchDate: string | null = null;
  selectedManager: string | null = null;
  constructor(
    private actionService: ActionService,
    private router: Router,
    private datePipe: DatePipe
  ){}
  ngOnInit(): void {
    this.getActions();
    this.selectedManager = localStorage.getItem('username');
    this.filterDateManager();
  }
  navigateToaAction(actionNumber: number) {
      this.router.navigate(['/edit_action', actionNumber]);
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
  filterDateManager(): void {
    this.selectedManager = localStorage.getItem('username');
    this.filteredActions = this.actions.filter(action => {
      const actionDate = this.datePipe.transform(action.dateAction, 'yyyy-MM-dd');
      const matchesDate = !this.searchDate || actionDate === this.searchDate;
      return matchesDate;
    });
  }
  newAction() {
    this.router.navigate(['/newAction']);
  }
  getActions(){
    this.actionService.getActions().subscribe(
      (res: any) => {
        this.actions = res;
        this.filteredActions = this.actions;
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

