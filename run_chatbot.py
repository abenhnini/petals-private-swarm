import torch
from transformers import AutoTokenizer, TextStreamer
from petals import AutoDistributedModelForCausalLM
from rich.console import Console
from rich.markdown import Markdown

# A modern, instruction-tuned model will give much better results.
# Llama-3-8B-Instruct: "meta-llama/Llama-3.1-8B-Instruct"
model_name = "meta-llama/Llama-3.1-8B-Instruct"

# You can also find public active peers on the Petals health monitor: https://health.petals.dev
INITIAL_PEERS = ['your_bootstrap_peer_id_here']

# How many past turns to keep in the conversation history to manage context length
MAX_HISTORY = 10

# Generation parameters
TEMPERATURE = 0.7
TOP_P = 0.9
DEVICE = 'cuda'

console = Console()

try:
    # Use the AutoTokenizer, which will handle chat templates correctly
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoDistributedModelForCausalLM.from_pretrained(
        model_name,
        initial_peers=INITIAL_PEERS,
        torch_dtype=torch.bfloat16, # Use bfloat16 for better performance
    )
    model = model.to(DEVICE)
    console.print("[green]Model and tokenizer loaded successfully![/green]")
except Exception as e:
    console.print(f"[bold red]Error loading model: {e}[/bold red]")
    exit()

# This object will handle printing the tokens to the console in real-time.
streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

conversation_history = []
# Main Chat Loop
console.print(Markdown("# Llama-3 Chatbot\n*Powered by Petals*"))
console.print("Type your message and press Enter. Type 'exit' or 'quit' to end the session.")

with model.inference_session(max_length=4096) as sess:
    while True:
        user_input = console.input("[bold cyan]You: [/bold cyan]")

        if user_input.lower() in ["exit", "quit"]:
            console.print("[bold yellow]Goodbye![/bold yellow]")
            break

        # Add the new user message to the history
        conversation_history.append({"role": "user", "content": user_input})

        # Keep the history from getting too long
        if len(conversation_history) > MAX_HISTORY * 2:
            conversation_history = conversation_history[-MAX_HISTORY*2:]

        # The tokenizer's `apply_chat_template` method correctly formats the entire
        # conversation history for the model. This is the most important step.
        inputs = tokenizer.apply_chat_template(
            conversation_history,
            return_tensors="pt"
        ).to(DEVICE)

        # Generate the full response at once
        console.print("[bold magenta]Assistant:[/bold magenta]", end="")
        outputs = model.generate(
            inputs,
            max_new_tokens=512,  # Max tokens for the assistant's reply
            do_sample=True,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            pad_token_id=tokenizer.eos_token_id,
            streamer=streamer,
            session=sess,
        )
        # We need a newline character after the streaming is done
        print()

        # Decode only the newly generated tokens
        new_tokens = outputs[0, inputs.shape[1]:]
        assistant_response = tokenizer.decode(new_tokens, skip_special_tokens=True)

        # Add the assistant's response to the history
        conversation_history.append({"role": "assistant", "content": assistant_response})

        # console.print(Markdown(assistant_response))
