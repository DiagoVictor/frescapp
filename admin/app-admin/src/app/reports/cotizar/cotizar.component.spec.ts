import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CotizarComponent } from './cotizar.component';

describe('CotizarComponent', () => {
  let component: CotizarComponent;
  let fixture: ComponentFixture<CotizarComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CotizarComponent]
    });
    fixture = TestBed.createComponent(CotizarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
