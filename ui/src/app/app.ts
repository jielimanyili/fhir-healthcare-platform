import { Component, inject, signal } from '@angular/core';
import { FhirService } from './services/fhir.service';
import { AuthService } from './services/auth.service';
import { Patient } from './models/fhir';

@Component({
  selector: 'app-root',
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App {
  private readonly fhir = inject(FhirService);
  readonly auth = inject(AuthService);

  protected readonly patients = signal<Patient[]>([]);
  protected readonly loading = signal(false);
  protected readonly error = signal('');

  protected readonly username = signal('');
  protected readonly password = signal('');
  protected readonly authError = signal('');

  login(): void {
    this.authError.set('');
    this.auth.login(this.username(), this.password()).subscribe({
      next: () => this.load(),
      error: () => this.authError.set('Login failed — check credentials.'),
    });
  }

  logout(): void {
    this.auth.logout();
    this.patients.set([]);
    this.error.set('');
  }

  load(): void {
    this.loading.set(true);
    this.error.set('');
    this.fhir.patients().subscribe({
      next: (bundle) => this.patients.set(bundle.entry?.map((e) => e.resource) ?? []),
      error: () => this.error.set('Failed to load patients.'),
      complete: () => this.loading.set(false),
    });
  }

  fullName(p: Patient): string {
    const name = p.name?.[0];
    return name ? `${name.given?.join(' ') ?? ''} ${name.family ?? ''}`.trim() : '';
  }
}
