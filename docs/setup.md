# Setup Guide

> Steps are in draft order — will be reordered later.

[← Back to README](../README.md)

---

## Create Models Directory

This directory is gitignored, so it won't exist after a fresh clone:

```bash
mkdir -p stack/models
```

## Download Local Models

Two models are used — a thinking model for deep reasoning and an instruct model for fast classification (e.g., prompt sanitization).

**Qwen3-4B Thinking** (~4.5 GB) — reasoning model:

```bash
curl -L -o stack/models/qwen3-4b-thinking-2507-q8_0.gguf \
  https://huggingface.co/ggml-org/Qwen3-4B-Thinking-2507-Q8_0-GGUF/resolve/main/qwen3-4b-thinking-2507-q8_0.gguf
```

**Qwen3-4B Instruct** (~4.3 GB) — fast non-thinking model:

```bash
curl -L -o stack/models/qwen3-4b-instruct-2507-q8_0.gguf \
  https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF/resolve/main/Qwen3-4B-Instruct-2507-Q8_0.gguf
```

> `stack/models/` is gitignored — model files stay local only.

## Configure Environment

```bash
cp stack/.env.example stack/.env
```

Edit `stack/.env` as needed.

## Install Frontend Dependencies

```bash
cd stack/frontend && npm install
```

## Start the Stack

```bash
cd stack && docker compose up -d
```

For development with exposed ports:

```bash
cd stack && docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```
