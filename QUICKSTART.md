# Wizelit SDK Quick Start Guide

Get your first Wizelit agent running in **under 30 minutes**. This guide takes approximately **5 minutes to read** and covers everything you need to build and deploy your first agent.

---

## What You'll Build

By the end of this guide, you'll have a working agent that:

- ✅ Exposes a reusable tool via REST API
- ✅ Runs locally or in a container
- ✅ Integrates with LLMs and other services

---

## Prerequisites

- Python 3.8+
- `pip` (Python package manager)
- A terminal/command line
- ~20 MB of disk space

---

## Step 1: Install the SDK

### Option A: Install from PyPI (Recommended)

```bash
pip install wizelit-sdk
```

### Option B: Install from Source (for development)

```bash
git clone https://github.com/wizelit/wizelit-sdk.git
cd wizelit-sdk
pip install -e .
```

**Verify installation:**

```bash
# The package provides the `wizelit-sdk` CLI. Use that or run the module directly:
wizelit-sdk --help
# or
python -m wizelit_sdk.cli --help
```

---

## Step 2: Create Your First Agent

Use the CLI to scaffold a new agent project (CLI is `wizelit-sdk`):

```bash
wizelit-sdk init my-first-agent
# Alternative (if you don't have the console script available):
python -m wizelit_sdk.cli init my-first-agent
# If you're running in an ephemeral `uv` environment:
uv run --with wizelit-sdk wizelit-sdk init my-first-agent
```

This creates a directory with:

```
my-first-agent/
├── main.py              # Your agent code
├── requirements.txt     # Dependencies
├── README.md           # Project docs
└── .env.example        # Environment template
```

**What just happened:** The `init` command generated a "fast" agent template (default). This is a lightweight, synchronous agent perfect for quick APIs.

---

## Step 3: Install Dependencies

Navigate to your project and install dependencies:

```bash
cd my-first-agent
pip install -r requirements.txt
```

---

## Step 4: Run Your Agent

Start the agent server:

```bash
python main.py
```

You should see output like:

```
INFO:     Uvicorn running on http://0.0.0.0:8080
```

🎉 **Your agent is now running!**

---

## Step 5: Test Your Agent

Open a **new terminal** while the agent is running.

### Test with curl:

```bash
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, Wizelit!"}'
```

**Expected response:**

```json
{ "echo": "Hello, Wizelit!" }
```

### Test with Python:

```python
import requests

response = requests.post(
    "http://localhost:8080/invoke",
    json={"text": "Hello, Wizelit!"}
)
print(response.json())
# Output: {"echo": "Hello, Wizelit!"}
```

---

## Step 6: Customize Your Agent

Edit `main.py` to add your own tools. Here's a simple example:

### Example: Text Analysis Tool

Replace the `example_tool` function with:

```python
@mcp.ingest(
    is_long_running=False,
    description="Analyze text sentiment and return statistics",
    response_handling={"mode": "json"},
)
def analyze_text(text: str) -> dict:
    """Analyze text and return word count and character count."""
    words = len(text.split())
    chars = len(text)
    return {
        "word_count": words,
        "char_count": chars,
        "avg_word_length": round(chars / words, 2) if words > 0 else 0
    }
```

### Restart and Test:

1. Stop your agent (Ctrl+C)
2. Restart:
   ```bash
   python main.py
   ```
3. Test the new tool:

   ```bash
   curl -X POST http://localhost:8080/invoke \
     -H "Content-Type: application/json" \
     -d '{"text": "The quick brown fox jumps over the lazy dog"}'
   ```

   **Response:**

   ```json
   {
     "word_count": 9,
     "char_count": 44,
     "avg_word_length": 4.89
   }
   ```

---

## Step 7: Explore Templates

Wizelit provides three agent templates:

### Fast Agent (Default)

- **Use case:** Simple, synchronous operations
- **Example:** Text processing, API proxying
- **Command:** `wizelit-sdk init my-agent --template fast`

### Slow Agent

- **Use case:** Long-running async tasks
- **Example:** File processing, ML inference, batch jobs
- **Includes:** Redis for job queuing
- **Command:** `wizelit-sdk init my-agent --template slow`

Example slow agent function:

```python
@mcp.ingest(is_long_running=True, description="Process large file")
async def process_file(filepath: str, job: Job) -> dict:
    job.logger.info(f"Starting to process {filepath}")
    # Your long-running work here
    return {"status": "complete"}
```

### Hybrid Agent

- **Use case:** Both fast and slow operations
- **Example:** API with background jobs
- **Command:** `wizelit-sdk init my-agent --template hybrid`

---

## Step 8: Validate Your Project

Ensure your agent has all required files:

```bash
wizelit-sdk validate
# or
python -m wizelit_sdk.cli validate
```

Output:

```
✅ Project looks valid
```

---

## Step 9: List Your Tools

See all tools available in your agent:

```bash
wizelit-sdk list-tools
# or
python -m wizelit_sdk.cli list-tools
```

Output:

```
- analyze_text (in main.py)
```

---

## Next Steps

### 1. **Add Environment Configuration**

Create a `.env` file from the template:

```bash
cp .env.example .env
```

For slow/hybrid agents with Redis:

```bash
REDIS_URL=redis://localhost:6379
ENABLE_LOG_STREAMING=true
```

### 2. **Deploy to Production**

- **Docker:** Add a `Dockerfile` (template coming soon)
- **Cloud:** Deploy to AWS Lambda, Google Cloud Run, etc.
- **MCP Server:** Use as a Model Context Protocol server

### 3. **Integrate with LLMs**

Register your agent with Claude, GPT, or other LLMs to use your tools.

### 4. **Advanced Features**

- Job tracking and streaming
- Multiple tool signatures
- Custom transport protocols
- Database integration

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'wizelit_sdk'"

```bash
# Reinstall the SDK
pip install --force-reinstall wizelit-sdk
```

### "Address already in use" (Port 8080)

```bash
# Use a different port
python main.py --port 8090
```

### Agent not responding

1. Check that the server is still running
2. Verify the endpoint URL is correct
3. Check logs for errors

---

## Examples & Resources

- **Example Agents:** See `dzun-local/examples/` in the repo
- **API Documentation:** See [API_DOCS.md](./API_DOCS.md)
- **Architecture Guide:** See [ARCHITECTURE.md](./ARCHITECTURE.md)
- **GitHub:** [wizelit/wizelit-sdk](https://github.com/wizelit/wizelit-sdk)

---

## Summary

You now know how to:

- ✅ Install Wizelit SDK
- ✅ Create agents with templates
- ✅ Run and test your agents locally
- ✅ Add custom tools
- ✅ Choose the right template for your use case

**Estimated time to get here: ~20-25 minutes** 🚀

---

## Questions?

- Check the [README.md](./README.md) for detailed docs
- Review [INITIALIZATION_INSTRUCTION.MD](./INITIALIZATION_INSTRUCTION.MD) for advanced setup
- Open an issue on GitHub

Happy building! 🎉
