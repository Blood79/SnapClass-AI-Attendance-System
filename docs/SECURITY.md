# Security checklist

- Keep secrets in environment variables or managed secrets, never Git.
- Use strong QR signing secrets and rotate them if exposed.
- Store password hashes, never plaintext passwords.
- Enforce HTTPS and secure session handling behind a production proxy.
- Configure and test Supabase Row Level Security before cloud deployment.
- Use least-privilege database credentials.
- Add rate limiting and account lockout around authentication endpoints.
- Log security events without storing raw biometric media.
- Validate QR expiry and signatures server-side.
- Add liveness and anti-spoofing before high-stakes biometric use.
