# EmailOpsEnv

## Description
Simulates real-world email triage and operations.

## Tasks
- spam_filter (easy)
- customer_support (medium)
- multi_step (hard)

## Run

```bash
docker build -t email-env .
docker run -p 7860:7860 email-env