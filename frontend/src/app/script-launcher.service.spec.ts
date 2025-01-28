import { TestBed } from '@angular/core/testing';

import { ScriptLauncherService } from './script-launcher.service';

describe('ScriptLauncherService', () => {
  let service: ScriptLauncherService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ScriptLauncherService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
