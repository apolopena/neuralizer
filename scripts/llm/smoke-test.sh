#!/bin/bash
# LLM Smoke Test — sends a prompt and displays the response with timings
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROMPT="${1:-Tell me a short story.}"
SPINNER="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

# Start the request in the background, capture output to temp file
TMPFILE=$(mktemp)
docker exec neuralizer-backend curl -s http://llm:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"qwen3-4b\",\"messages\":[{\"role\":\"user\",\"content\":\"$PROMPT\"}]}" \
  > "$TMPFILE" &
PID=$!

# Show prompt and spinner
echo -e "${YELLOW}Sent Prompt:${NC} $PROMPT"
echo -ne "${BLUE}Waiting for LLM inference... ${NC}"
i=0
while kill -0 "$PID" 2>/dev/null; do
  echo -ne "\b${SPINNER:i++%${#SPINNER}:1}"
  sleep 0.1
done
echo -e "\b${GREEN}done${NC}"
echo ""

wait "$PID"

# Parse and display
python3 -c "
import json, sys
with open('$TMPFILE') as f:
    d = json.load(f)
msg = d['choices'][0]['message']
t = d.get('timings', {})
u = d.get('usage', {})

# Thinking (if present)
if msg.get('reasoning_content'):
    print('\033[1;33m--- THINKING ---\033[0m')
    print(msg['reasoning_content'].strip())
    print()

# Response
print('\033[0;32m--- RESPONSE ---\033[0m')
print(msg.get('content', '').strip() or '(empty — increase max_tokens or model used all tokens on thinking)')
print()

# Usage + Timings
print('\033[0;34m--- STATS ---\033[0m')
print(f\"Prompt tokens:     {u.get('prompt_tokens', '?')}\")
print(f\"Completion tokens: {u.get('completion_tokens', '?')}\")
print(f\"Total tokens:      {u.get('total_tokens', '?')}\")
if t:
    print(f\"Prompt speed:      {t.get('prompt_per_second', 0):.1f} t/s\")
    print(f\"Generation speed:  {t.get('predicted_per_second', 0):.1f} t/s\")
    print(f\"Generation time:   {t.get('predicted_ms', 0) / 1000:.1f}s\")
"

rm -f "$TMPFILE"
