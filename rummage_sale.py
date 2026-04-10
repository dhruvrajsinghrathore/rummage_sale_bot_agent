#!/usr/bin/env python3
"""
Rummage Sale Chat Agent — Main Entry Point
A CLI chat agent using Ollama's local LLM with tool-calling.
The LLM acts as Eddie, an electronics garage sale seller.
"""

import sys
import signal
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from state import load_state, save_state
from agent import create_agent, run_agent_turn


console = Console()


def display_welcome_banner(is_returning: bool, state: dict):
    """Display a welcome banner with sale info."""
    banner = Text()
    banner.append("🔌 EDDIE'S ELECTRONICS GARAGE SALE 🔌\n", style="bold cyan")
    banner.append("Browse, Haggle, Score Deals!", style="italic yellow")

    console.print()
    console.print(Panel(banner, border_style="bright_cyan", padding=(1, 4)))
    console.print()

    if is_returning:
        sold_count = sum(1 for item in state["inventory"] if item["sold"])
        unsold_count = sum(1 for item in state["inventory"] if not item["sold"])
        console.print(
            f"  [dim]Welcome back! {sold_count} items sold so far, {unsold_count} still available.[/dim]"
        )
    else:
        total = len(state["inventory"])
        console.print(
            f"  [dim]Fresh sale! {total} electronics items ready to go.[/dim]"
        )

    console.print(f"  [dim]Model: {OLLAMA_MODEL} via Ollama ({OLLAMA_BASE_URL})[/dim]")
    console.print(
        "  [dim]Type [bold]quit[/bold] or [bold]exit[/bold] to leave. Ctrl+C also works.[/dim]"
    )
    console.print()


def display_response(text: str):
    """Display the agent's response with formatting."""
    console.print()
    try:
        md = Markdown(text)
        console.print(Panel(md, title="[bold green]Eddie[/bold green]", border_style="green", padding=(0, 2)))
    except Exception:
        console.print(Panel(text, title="[bold green]Eddie[/bold green]", border_style="green", padding=(0, 2)))
    console.print()


def main():
    """Main chat loop."""
    # Load state
    state = load_state()

    # Check if this is a returning session
    is_returning = len(state["transactions"]) > 0

    # Display welcome
    display_welcome_banner(is_returning, state)

    # Initialize Ollama client
    try:
        console.print("  [dim]Connecting to Ollama...[/dim]")
        client = create_agent()
        console.print("  [dim green]✓ Connected![/dim green]\n")
    except Exception as e:
        console.print(f"[bold red]Error connecting to Ollama:[/bold red] {e}")
        console.print("[dim]Make sure Ollama is running: ollama serve[/dim]")
        sys.exit(1)

    # Chat history for conversation context
    chat_history = []

    # Send an initial hidden message to get Eddie to introduce himself
    initial_prompt = (
        "A new customer just walked up to your garage sale table. "
        "Greet them warmly and let them know what you've got today. "
        "Check the sale status first to know the time."
    )
    if is_returning:
        initial_prompt = (
            "A customer is back at your garage sale! "
            "Welcome them back. Check the sale status to know the time, "
            "and let them know what's still available."
        )

    try:
        console.print("  [dim]Eddie is getting ready...[/dim]")
        response_text, chat_history = run_agent_turn(
            client, chat_history, initial_prompt, state
        )
        display_response(response_text)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("[dim]Make sure Ollama is running and the model is pulled.[/dim]")
        console.print(f"[dim]Run: ollama pull {OLLAMA_MODEL}[/dim]\n")
        # Continue anyway — let user try chatting
        console.print("[dim]Starting without intro. Just start chatting![/dim]\n")

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        console.print("\n")
        console.print(
            Panel(
                "[yellow]Thanks for stopping by! See you next time! 👋[/yellow]",
                border_style="yellow",
            )
        )
        save_state(state)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Main chat loop
    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ").strip()
        except EOFError:
            break

        # Exit commands
        if user_input.lower() in ("quit", "exit", "bye", "q"):
            console.print()
            console.print(
                Panel(
                    "[yellow]Thanks for shopping at Eddie's! Come back anytime! 🔌👋[/yellow]",
                    border_style="yellow",
                )
            )
            save_state(state)
            break

        # Skip empty input
        if not user_input:
            continue

        # Run agent turn
        try:
            response_text, chat_history = run_agent_turn(
                client, chat_history, user_input, state
            )
            display_response(response_text)
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {e}")
            console.print("[dim]Try again or type 'quit' to exit.[/dim]\n")

    console.print()


if __name__ == "__main__":
    main()
