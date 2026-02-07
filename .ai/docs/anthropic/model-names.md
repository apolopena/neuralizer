# Anthropic Model Names

> Retrieved via Anthropic API on 2026-02-07
> ```bash
> set -a && source .env && set +a && curl -s https://api.anthropic.com/v1/models -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" | jq '.data[].id'
> ```

## Opus

| Model ID | Notes |
|----------|-------|
| `claude-opus-4-6` | Latest Opus (4.6) |
| `claude-opus-4-5-20251101` | Opus 4.5 |
| `claude-opus-4-1-20250805` | Opus 4.1 |
| `claude-opus-4-20250514` | Opus 4.0 |

## Sonnet

| Model ID | Notes |
|----------|-------|
| `claude-sonnet-4-5-20250929` | Latest Sonnet (4.5) |
| `claude-sonnet-4-20250514` | Sonnet 4.0 |
| `claude-3-7-sonnet-20250219` | Sonnet 3.7 |

## Haiku

| Model ID | Notes |
|----------|-------|
| `claude-haiku-4-5-20251001` | Latest Haiku (4.5) |
| `claude-3-5-haiku-20241022` | Haiku 3.5 |
| `claude-3-haiku-20240307` | Haiku 3.0 |
