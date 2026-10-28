import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Bundle, Claim, Observation, Patient } from '../models/fhir';

@Injectable({ providedIn: 'root' })
export class FhirService {
  private readonly http = inject(HttpClient);

  patients(family?: string): Observable<Bundle<Patient>> {
    const params = family ? { family } : undefined;
    return this.http.get<Bundle<Patient>>('/fhir/Patient', { params });
  }

  observations(subject: string): Observable<Bundle<Observation>> {
    return this.http.get<Bundle<Observation>>('/fhir/Observation', { params: { subject } });
  }

  claims(patient: string): Observable<Bundle<Claim>> {
    return this.http.get<Bundle<Claim>>('/fhir/Claim', { params: { patient } });
  }
}
