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
cp stack/.env.sample stack/.env
```

Edit `stack/.env` to select your GPU backend and ports. The `COMPOSE_FILE` variable controls which Docker Compose override files are layered:

- **NVIDIA CUDA** (default): `COMPOSE_FILE=docker-compose.yml:docker-compose.cuda.yml`
- **AMD/Intel Vulkan**: `COMPOSE_FILE=docker-compose.yml:docker-compose.vulkan.yml`
- **CPU-only**: `COMPOSE_FILE=docker-compose.yml:docker-compose.cpu.yml`

For HTTPS, add `docker-compose.https.yml` to `COMPOSE_FILE` and set `CADDYFILE=Caddyfile.https`.

## Install Frontend Dependencies

```bash
cd stack/frontend && npm install
```

## Start the Stack

```bash
./scripts/stack.sh up
```

Or directly from the stack directory:

```bash
cd stack && docker compose up -d
```

For development with exposed ports, add `docker-compose.dev.yml` to `COMPOSE_FILE` in `.env`:

```
COMPOSE_FILE=docker-compose.yml:docker-compose.cuda.yml:docker-compose.dev.yml
```

## Server Deployments

For remote servers where Vite env injection may not set the iframe URL correctly, use the bootstrap script:

```bash
./scripts/bootstrap-iframe.sh --host 192.168.1.50
```
