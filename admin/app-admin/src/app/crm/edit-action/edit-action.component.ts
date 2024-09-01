import { Component, OnInit } from '@angular/core';
import { ActionService } from '../../services/action.service';
import { Router, ActivatedRoute } from '@angular/router';
import * as mapboxgl from 'mapbox-gl';

@Component({
  selector: 'app-edit-action',
  templateUrl: './edit-action.component.html',
  styleUrl: './edit-action.component.css'
})
export class EditActionComponent implements OnInit {
  actionObject: any = {
    dateAction: '',
    dateSolution: '',
    type: '',
    customer: {},
    orderNumber: '',
    manager: '',
    status: '',
    actionComment: '',
    solutionType: '',
    solutionComment: '',
    latitude: null,   
    longitude: null   
  };

  solutions: string[] = [];
  public map: any;

  constructor(
    private actionService: ActionService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.loadAction();
    this.getCurrentLocation();  // Obtener ubicación del dispositivo
  }

  loadAction() {
    const actionId = this.route.snapshot.paramMap.get('action');
    if (actionId) {
      this.actionService.getAction(actionId).subscribe(
        (data) => {
          this.actionObject = data;
          this.solutions = data.type.solutions;
          this.initializeMap();  // Inicializa el mapa con la posición del customer
        },
        (error) => {
          console.error('Error al cargar la acción:', error);
        }
      );
    }
  }

  initializeMap() {
    if (this.actionObject.customer.latitude && this.actionObject.customer.longitude) {
      this.map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/streets-v12',
        projection: { name: 'mercator' },
        zoom: 15,
        center: [
          parseFloat(this.actionObject.customer.longitude),
          parseFloat(this.actionObject.customer.latitude)
        ],
        accessToken: "pk.eyJ1Ijoidm1kaWFnb3YiLCJhIjoiY2x4MGtxY2NlMDFxdDJycTdrdXhvYWE4byJ9.rQb2uBaS48sEyvpbdMj14Q"
      });

      new mapboxgl.Marker()
        .setLngLat([
          parseFloat(this.actionObject.customer.longitude),
          parseFloat(this.actionObject.customer.latitude)
        ])
        .addTo(this.map);
    }
  }

  getCurrentLocation() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.actionObject.latitude = position.coords.latitude;
          this.actionObject.longitude = position.coords.longitude;
        },
        (error) => {
          console.error('Error obteniendo la ubicación:', error);
        }
      );
    } else {
      console.error('Geolocalización no es soportada por el navegador');
    }
  }

  backList() {
    this.router.navigate(['/crm']);
  }

  completar() {
    const bogotaTime = new Date().toLocaleString("en-US", { timeZone: "America/Bogota" });
    this.actionObject.dateSolution = new Date(bogotaTime).toISOString(); // Convertir a formato ISO
    
    this.actionObject.status = 'Completada';
    
    this.getCurrentLocation();

    this.actionService.editAction(this.actionObject.actionNumber, this.actionObject).subscribe((res) => {
      this.router.navigate(['/crm']);
    });
}

}
