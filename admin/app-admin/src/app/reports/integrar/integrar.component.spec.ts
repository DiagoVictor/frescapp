import { ComponentFixture, TestBed } from '@angular/core/testing';

import { IntegrarComponent } from './integrar.component';

describe('IntegrarComponent', () => {
  let component: IntegrarComponent;
  let fixture: ComponentFixture<IntegrarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IntegrarComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(IntegrarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
