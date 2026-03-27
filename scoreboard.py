# scoreboard.py

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

def display_scoreboard(match_state):
    """Displays the live scoreboard in the terminal."""

    console.clear()

    # ── Title ──────────────────────────────────────────────────────────────
    console.print(Panel(
        Text("LEGENDS OF CRICKET", justify="center", style="bold yellow"),
        style="bold yellow"
    ))

    # ── Match info ─────────────────────────────────────────────────────────
    console.print(f"\n[bold cyan]Day {match_state['day']} — Session {match_state['session']}[/bold cyan]")
    console.print(f"[white]{match_state['batting_team']}[/white] vs [white]{match_state['fielding_team']}[/white]\n")

    # ── Scorecard table ────────────────────────────────────────────────────
    table = Table(box=box.SIMPLE_HEAVY, style="cyan", header_style="bold magenta")
    table.add_column("Batting", style="white", min_width=20)
    table.add_column("R",  justify="right", style="yellow")
    table.add_column("B",  justify="right", style="white")
    table.add_column("SR", justify="right", style="green")

    for batter in match_state["batters_at_crease"]:
        sr = round((batter["runs"] / batter["balls"]) * 100, 1) if batter["balls"] > 0 else 0.0
        table.add_row(
            f"{'⭐ ' if batter.get('star') else ''}{batter['name']}{'*' if batter.get('not_out') else ''}",
            str(batter["runs"]),
            str(batter["balls"]),
            str(sr)
        )

    console.print(table)

    # ── Totals ─────────────────────────────────────────────────────────────
    score = match_state["score"]
    console.print(
        f"[bold yellow]Score:[/bold yellow] "
        f"[bold white]{score['runs']}/{score['wickets']}[/bold white]  "
        f"[bold yellow]Overs:[/bold yellow] [white]{score['overs']}[/white]  "
        f"[bold yellow]RR:[/bold yellow] [white]{score['run_rate']}[/white]\n"
    )

    # ── Current bowler ─────────────────────────────────────────────────────
    bowler = match_state.get("current_bowler")
    if bowler:
        console.print(
            f"[bold magenta]Bowling:[/bold magenta] "
            f"[white]{bowler['name']}[/white]  "
            f"[yellow]{bowler['overs']}ov  "
            f"{bowler['wickets']}w  "
            f"{bowler['runs']}r[/yellow]\n"
        )

    # ── Target (second innings) ────────────────────────────────────────────
    if match_state.get("target"):
        needed = match_state["target"] - score["runs"]
        console.print(
            f"[bold red]Target:[/bold red] [white]{match_state['target']}[/white]  "
            f"[bold red]Need:[/bold red] [white]{needed} runs[/white]\n"
        )


def display_commentary(line):
    """Prints a single commentary line."""
    console.print(f"[italic dim white]  ▶  {line}[/italic dim white]")


def display_session_summary(session_stats):
    """Shows a summary panel between sessions."""
    console.print(Panel(
        f"[bold]Session Summary[/bold]\n"
        f"Runs scored: [yellow]{session_stats['runs']}[/yellow]\n"
        f"Wickets lost: [red]{session_stats['wickets']}[/red]\n"
        f"Overs bowled: [cyan]{session_stats['overs']}[/cyan]",
        title="[bold magenta]End of Session[/bold magenta]",
        style="magenta"
    ))


def display_day_summary(day, score):
    """Shows end of day summary."""
    console.print(Panel(
        f"[bold]Stumps drawn — Day {day}[/bold]\n"
        f"Score: [yellow]{score['runs']}/{score['wickets']}[/yellow]  "
        f"Overs: [cyan]{score['overs']}[/cyan]",
        title="[bold yellow] End of Day[/bold yellow]",
        style="yellow"
    ))


def display_match_result(result):
    """Final match result screen."""
    console.print(Panel(
        Text(result, justify="center", style="bold white"),
        title="[bold green] MATCH RESULT[/bold green]",
        style="bold green"
    ))


def prompt_strategy():
    """Asks the player to choose a batting strategy."""
    console.print("\n[bold cyan]Choose your batting strategy:[/bold cyan]")
    console.print("  [yellow]1[/yellow] — Aggressive 🔥  (more runs, more risk)")
    console.print("  [yellow]2[/yellow] — Balanced ⚖️   (steady play)")
    console.print("  [yellow]3[/yellow] — Defensive 🛡️  (protect wickets)\n")

    choice = input("Your choice (1/2/3): ").strip()
    mapping = {"1": "aggressive", "2": "balanced", "3": "defensive"}
    return mapping.get(choice, "balanced")
