# OIDC / SSO Integration Baseline

This template describes the minimum contract for applications integrating with an external OIDC provider such as Keycloak, Authentik, Entra ID, or another standards-compliant IdP.

```yaml
issuer: https://idp.example.com/realms/project
client:
  auth_method: oidc
  redirect_uris:
    - https://app.example.com/oauth2/callback
  scopes:
    - openid
    - profile
    - email
session:
  max_age: 8h
  secure_cookie: true
  same_site: Lax
authorization:
  map_claims:
    subject: sub
    username: preferred_username
    groups: groups
```

## Integration rules

- Never hard-code client secrets in source control.
- Validate issuer, audience, signature, expiry, nonce/state, and redirect URI.
- Prefer group/role claims over application-local duplicated identities.
- Keep authentication and authorization policy distinct.
- Document logout/session invalidation behavior.
- Provide a local development mode without weakening production validation.
- Record required IdP configuration in deployment documentation.
