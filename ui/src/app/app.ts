import { Component, inject, signal } from '@angular/core';
import { FhirService } from './services/fhir.service';
import { Patient } from './models/fhir';

@Component({
  selector: 'app-root',
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App {
  private readonly fhir = inject(FhirService);

  protected readonly patients = signal<Patient[]>([]);
  protected readonly loading = signal(false);
  protected readonly error = signal('');

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set('');
    this.fhir.patients().subscribe({
      next: (bundle) => this.patients.set(bundle.entry?.map((e) => e.resource) ?? []),
      error: () => this.error.set('Failed to load patients — is the API running on :8000?'),
      complete: () => this.loading.set(false),
    });
  }

  fullName(p: Patient): string {
    const name = p.name?.[0];
    return name ? `${name.given?.join(' ') ?? ''} ${name.family ?? ''}`.trim() : '';
  }
}
