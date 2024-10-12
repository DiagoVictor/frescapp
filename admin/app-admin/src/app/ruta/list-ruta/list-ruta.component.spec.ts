import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListRutaComponent } from './list-ruta.component';

describe('ListRutaComponent', () => {
  let component: ListRutaComponent;
  let fixture: ComponentFixture<ListRutaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListRutaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListRutaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
