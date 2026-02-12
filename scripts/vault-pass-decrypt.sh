#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENC_FILE="${VAULT_PASS_ENC_FILE:-${ROOT_DIR}/inventory/vault-pass.enc}"

if [[ ! -f "${ENC_FILE}" ]]; then
  echo "Encrypted vault password file not found: ${ENC_FILE}" >&2
  echo "Run scripts/vault-pass-encrypt.sh to create it." >&2
  exit 1
fi

if [[ -z "${VAULT_PASS_DECRYPT_KEY:-}" ]]; then
  echo "Set VAULT_PASS_DECRYPT_KEY before using this script." >&2
  exit 1
fi

DECRYPTED_PASSWORD="$(
  openssl enc -d -aes-256-cbc -pbkdf2 -md sha256 -a \
    -pass env:VAULT_PASS_DECRYPT_KEY \
    -in "${ENC_FILE}" 2>/dev/null
)"

if [[ "${DECRYPTED_PASSWORD}" == "CHANGE_ME_VAULT_PASSWORD" ]]; then
  echo "inventory/vault-pass.enc still contains placeholder data." >&2
  echo "Run scripts/vault-pass-encrypt.sh with your real vault password." >&2
  exit 1
fi

printf '%s' "${DECRYPTED_PASSWORD}"
