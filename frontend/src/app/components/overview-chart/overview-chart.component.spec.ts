import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OverviewChartComponent } from './overview-chart.component';

describe('OverviewChartComponent', () => {
  let component: OverviewChartComponent;
  let fixture: ComponentFixture<OverviewChartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OverviewChartComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OverviewChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
