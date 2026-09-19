# Biometric privacy

Face and voice features are optional because biometric data requires stronger controls than ordinary application data.

## Data minimization

The prototype is designed around derived feature vectors and does not require raw photos or audio to be committed to the repository. Derived vectors should still be treated as sensitive biometric information.

## Before production

Define explicit notice and consent, purpose limitation, retention and deletion schedules, access controls, encryption, incident response, and a process for false matches and false rejects.

Verification thresholds are engineering parameters, not proof of identity. Calibrate them on representative validation data and document the operating point.
