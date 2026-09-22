#!/usr/bin/env bash
set -euo pipefail

section() { printf '\n== %s ==\n' "$1"; }

section "Host"
printf 'kernel: %s\n' "$(uname -sr)"
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  printf 'os: %s\n' "${PRETTY_NAME:-unknown}"
fi

section "Linux Security Module"
if command -v getenforce >/dev/null 2>&1; then
  printf 'selinux: %s\n' "$(getenforce 2>/dev/null || true)"
elif [[ -r /sys/fs/selinux/enforce ]]; then
  printf 'selinux: %s\n' "$(cat /sys/fs/selinux/enforce 2>/dev/null || true)"
else
  printf 'selinux: not detected\n'
fi

if command -v aa-status >/dev/null 2>&1; then
  aa-status 2>/dev/null || true
else
  printf 'apparmor: aa-status not available\n'
fi

section "OS Firewall"
if command -v firewall-cmd >/dev/null 2>&1; then
  printf 'firewalld-state: %s\n' "$(firewall-cmd --state 2>/dev/null || true)"
fi
if command -v ufw >/dev/null 2>&1; then
  ufw status 2>/dev/null || true
fi
if command -v nft >/dev/null 2>&1; then
  printf 'nftables: available\n'
  nft list ruleset >/dev/null 2>&1 && printf 'nftables-ruleset: readable\n' || printf 'nftables-ruleset: unavailable without additional privilege\n'
fi

section "Runtime prerequisites"
for cmd in containerd crio kubelet cilium; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '%s: available\n' "$cmd"
  fi
done

printf '\nInspection only: this script does not change firewall, LSM, or Kubernetes state.\n'
