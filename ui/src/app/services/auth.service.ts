import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs';

export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  expires_in?: number;
  token_type?: string;
}

/**
 * Demo OIDC login via Keycloak's resource-owner password grant against the
 * public `fhir-ui` client (no client secret in the SPA). Production would use
 * the authorization-code + PKCE flow; this keeps the demo self-contained.
 */
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);

  readonly token = signal('');
  readonly user = signal('');

  login(username: string, password: string) {
    const body = new URLSearchParams({
      grant_type: 'password',
      client_id: 'fhir-ui',
      username,
      password,
    }).toString();

    return this.http
      .post<TokenResponse>('/auth/realms/fhir/protocol/openid-connect/token', body, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      .pipe(
        tap((res) => {
          this.token.set(res.access_token);
          this.user.set(username);
        }),
      );
  }

  logout(): void {
    this.token.set('');
    this.user.set('');
  }
}
