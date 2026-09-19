# Architecture

SnapClass has four layers: UI, application services, biometric adapters, and persistence.

1. UI: Streamlit for teacher/student workflows and Flask for the product landing page.
2. Services: attendance rules, authentication, QR signing and verification.
3. Biometric adapters: face and voice modules that can be installed independently from the core app.
4. Persistence: local JSON for demos plus a documented Supabase/PostgreSQL schema.

The design goal is replaceability. A new biometric model or database should not require rewriting attendance rules.

## Verification pipeline

Face: image → face descriptor → nearest known descriptor → distance threshold → accepted/rejected.

Voice: audio → MFCC/delta summary → normalized vector → cosine similarity → threshold → accepted/rejected.

Thresholds are configuration values. A production system must calibrate them using representative validation data.
