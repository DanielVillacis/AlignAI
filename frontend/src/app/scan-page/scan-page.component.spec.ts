import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ScanPageComponent } from './scan-page.component';

describe('ScanPageComponent', () => {
  let component: ScanPageComponent;
  let fixture: ComponentFixture<ScanPageComponent>;

  beforeEach(async () => {
      await TestBed.configureTestingModule({
        imports: [ScanPageComponent],
      }).compileComponents();
    });
  
    it('should create the app', () => {
      const fixture = TestBed.createComponent(ScanPageComponent);
      const app = fixture.componentInstance;
      expect(app).toBeTruthy();
    });
  
    it('should render title', () => {
      const fixture = TestBed.createComponent(ScanPageComponent);
      fixture.detectChanges();
      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.querySelector('h1')?.textContent).toContain('Hello, frontend');
    });
});
