import gradio as gr
from loguru import logger
import time
import traceback
import os

# -----------------------------------------------------------
# Try to import run_agent from your project's main_agent.py
# -----------------------------------------------------------
try:
    from project.main_agent import run_agent   # MUST exist in your repo
except Exception as e:
    # Fallback stub shown if import fails
    def run_agent(user_input: str) -> str:
        return (
            "[ERROR] Could not import project.main_agent.run_agent().\n"
            "Fix your repository or ensure main_agent.py defines run_agent(user_input).\n"
            f"Import error: {e}"
        )

# -----------------------------------------------------------
# Logging setup
# -----------------------------------------------------------
LOG_FILE = "spaces_app.log"

logger.remove()
logger.add(
    LOG_FILE,
    format="{message}",
    serialize=True,
    level="INFO",
    enqueue=True
)

def append_log(entry: dict):
    """Write structured JSON to spaces_app.log"""
    try:
        logger.info(entry)
    except Exception:
        logger.error({"time": time.time(), "msg": "Failed to log entry"})

def tail_logs(max_lines=300):
    """Return last N lines of the log file."""
    if not os.path.exists(LOG_FILE):
        return ""

    with open(LOG_FILE, "r") as f:
        lines = f.readlines()[-max_lines:]
    return "".join(lines)

# -----------------------------------------------------------
# Format conversation history to Markdown
# -----------------------------------------------------------
def format_conversation(history):
    md = []
    for msg in history:
        md.append(f"**User:** {msg['user']}\n")
        md.append(f"**Assistant:** {msg['assistant']}\n")
    return "\n".join(md) if md else "No conversation yet. Say hi!"

# -----------------------------------------------------------
# Main submit function for Gradio
# -----------------------------------------------------------
def submit(user_input, history):
    ts = time.time()

    append_log({
        "event": "request_received",
        "ts": ts,
        "input": user_input
    })

    try:
        output = run_agent(user_input)
        append_log({
            "event": "response_generated",
            "ts": time.time(),
            "output": str(output)[:1000]
        })

    except Exception as e:
        output = "ERROR: " + str(e) + "\n" + traceback.format_exc()
        append_log({
            "event": "response_error",
            "ts": time.time(),
            "error": str(e)
        })

    history = history or []
    history.append({
        "user": user_input,
        "assistant": output,
        "ts": ts
    })

    return (
        format_conversation(history),
        history,
        tail_logs()
    )

# -----------------------------------------------------------
# Clear button
# -----------------------------------------------------------
def clear_history():
    return "No conversation yet. Say hi!", [], tail_logs()

# -----------------------------------------------------------
# Gradio UI
# -----------------------------------------------------------
with gr.Blocks(title="Multi‑Agent System UI") as demo:

    gr.Markdown("## 🚀 Multi‑Agent System — Hugging Face Space")

    with gr.Row():
        with gr.Column(scale=2):
            conversation = gr.Markdown("No conversation yet. Say hi!")
        with gr.Column(scale=1):
            logs_box = gr.Textbox(
                label="Live Logs (spaces_app.log)",
                value=tail_logs(),
                lines=25
            )

    user_input = gr.Textbox(label="Your input")
    submit_btn = gr.Button("Send")
    clear_btn = gr.Button("Clear Conversation")

    history_state = gr.State([])

    submit_btn.click(
        submit,
        inputs=[user_input, history_state],
        outputs=[conversation, history_state, logs_box]
    )

    clear_btn.click(
        clear_history,
        inputs=None,
        outputs=[conversation, history_state, logs_box]
    )

demo.launch(server_name="0.0.0.0", server_port=7860)