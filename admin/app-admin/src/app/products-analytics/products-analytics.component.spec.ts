import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProductsAnalyticsComponent } from './products-analytics.component';

describe('ProductsAnalyticsComponent', () => {
  let component: ProductsAnalyticsComponent;
  let fixture: ComponentFixture<ProductsAnalyticsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProductsAnalyticsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProductsAnalyticsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
