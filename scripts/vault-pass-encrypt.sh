#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENC_FILE="${VAULT_PASS_ENC_FILE:-${ROOT_DIR}/inventory/vault-pass.enc}"

if [[ -z "${VAULT_PASS_DECRYPT_KEY:-}" ]]; then
  echo "Set VAULT_PASS_DECRYPT_KEY before running this script." >&2
  exit 1
fi

read -rsp "Enter Ansible Vault password to encrypt: " VAULT_PASSWORD
printf '\n' >&2

if [[ -z "${VAULT_PASSWORD}" ]]; then
  echo "Vault password cannot be empty." >&2
  exit 1
fi

umask 077
printf '%s' "${VAULT_PASSWORD}" | openssl enc -aes-256-cbc -pbkdf2 -md sha256 -a \
  -pass env:VAULT_PASS_DECRYPT_KEY \
  -out "${ENC_FILE}"

echo "Encrypted vault password written to ${ENC_FILE}" >&2
