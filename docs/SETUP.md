# Setup

## Core demo

Create a virtual environment, install requirements-core.txt, then run the Streamlit app. Full requirements.txt also installs the optional biometric stack.

Demo accounts created on first launch:

- teacher@snapclass.local / teacher123
- student@snapclass.local / student123

Change or remove demo credentials before deployment.

## Optional biometric stack

Install requirements-biometric.txt for face and voice verification. Face uses the face_recognition Python package behind an adapter. Voice uses librosa MFCC and delta features.

## Environment

Copy .env.example to .env and replace SNAPCLASS_QR_SECRET with a long random value for any non-demo environment.
