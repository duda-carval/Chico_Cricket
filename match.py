# match.py

import random
import time
from teams import players
from ball import simulate_ball, get_commentary
from scoreboard import (
    display_scoreboard,
    display_commentary,
    display_session_summary,
    display_day_summary,
    display_match_result,
    prompt_strategy,
    console
)

# ── Constants ──────────────────────────────────────────────────────────────────

OVERS_PER_SESSION = 30   # 3 sessions per day × 30 overs = 90 overs/day
SESSIONS_PER_DAY  = 3
MAX_DAYS          = 5
SESSION_NAMES     = ["Morning", "Afternoon", "Evening"]

# ── Team selection ─────────────────────────────────────────────────────────────

def select_team(player_names, team_name):
    """Lets the player pick their XI from the available pool."""
    console.print(f"\n[bold yellow]Select your {team_name} XI[/bold yellow]")
    console.print("[dim]Available players:[/dim]\n")

    pool = list(player_names)
    for i, name in enumerate(pool, 1):
        p = players[name]
        console.print(
            f"  [yellow]{i:>2}.[/yellow] [white]{name:<25}[/white] "
            f"[cyan]{p['country']:<15}[/cyan] "
            f"[magenta]{p['role']}[/magenta]"
        )

    console.print("\n[bold cyan]Enter 11 numbers separated by commas (e.g. 1,3,5,7,9,11,13,15,16,17,18):[/bold cyan]")
    
    while True:
        raw = input("> ").strip()
        try:
            picks = [int(x.strip()) for x in raw.split(",")]
            if len(picks) != 11:
                console.print("[red]Please pick exactly 11 players.[/red]")
                continue
            if len(set(picks)) != 11:
                console.print("[red]No duplicates please![/red]")
                continue
            if any(p < 1 or p > len(pool) for p in picks):
                console.print(f"[red]Numbers must be between 1 and {len(pool)}.[/red]")
                continue
            selected = [pool[p - 1] for p in picks]
            return selected
        except ValueError:
            console.print("[red]Invalid input. Use numbers separated by commas.[/red]")


def ai_select_team(remaining_pool):
    """AI picks its XI from whatever players are left."""
    return random.sample(remaining_pool, 11)


def build_player(name, index):
    """Returns a full player dict with name + stats merged."""
    p = players[name].copy()
    p["name"] = name
    p["batting_index"] = index
    p["runs"] = 0
    p["balls"] = 0
    p["not_out"] = True
    p["star"] = name in ["Sachin Tendulkar", "Shane Warne"]
    return p


# ── Innings logic ──────────────────────────────────────────────────────────────

def run_session(batting_xi, bowling_xi, score, match_state, target=None):
    """
    Runs one session (up to OVERS_PER_SESSION overs).
    Returns updated score and whether innings is still ongoing.
    """

    session_runs    = 0
    session_wickets = 0
    session_overs   = 0

    batters  = [build_player(n, i) for i, n in enumerate(batting_xi)]
    bowlers  = [build_player(n, i) for i, n in enumerate(bowling_xi)]

    # Start with top two batters
    on_strike    = batters[score["wickets"]]
    non_striker  = batters[min(score["wickets"] + 1, 10)]
    next_batter  = score["wickets"] + 2

    # Pick opening bowler (highest bowling skill)
    current_bowler = max(bowlers, key=lambda b: b["bowling_skill"])
    current_bowler["overs"] = 0
    current_bowler["wickets"] = 0
    current_bowler["runs"] = 0

    strategy = prompt_strategy()

    for over in range(OVERS_PER_SESSION):
        if score["wickets"] >= 10:
            return score, session_runs, session_wickets, session_overs, False

        if target and score["runs"] >= target:
            return score, session_runs, session_wickets, session_overs, False

        balls_in_over = 0

        for ball in range(6):
            result = simulate_ball(on_strike, current_bowler, strategy)

            # Update batter
            on_strike["runs"]  += result["runs"]
            on_strike["balls"] += 1

            # Update bowler
            current_bowler["runs"] += result["runs"]

            # Update score
            score["runs"] += result["runs"]

            # Update match state for display
            match_state["batters_at_crease"] = [on_strike, non_striker]
            match_state["current_bowler"]    = current_bowler
            match_state["score"]             = {
                "runs":     score["runs"],
                "wickets":  score["wickets"],
                "overs":    f"{score['overs']}.{balls_in_over}",
                "run_rate": round(score["runs"] / max(score["overs"] + 0.1, 0.1), 2),
            }
            if target:
                match_state["target"] = target

            display_scoreboard(match_state)
            display_commentary(result["commentary"])
            time.sleep(0.6)

            if result["outcome"] == "wicket":
                score["wickets"] += 1
                session_wickets  += 1
                current_bowler["wickets"] += 1
                on_strike["not_out"] = False

                if score["wickets"] >= 10:
                    break

                if next_batter <= 10:
                    on_strike   = batters[next_batter]
                    next_batter += 1

            else:
                # Rotate strike on odd runs
                if result["runs"] % 2 == 1:
                    on_strike, non_striker = non_striker, on_strike

            balls_in_over += 1

        # End of over — rotate strike, change bowler
        on_strike, non_striker = non_striker, on_strike
        score["overs"] += 1
        session_overs  += 1
        current_bowler["overs"] += 1

        # Swap bowler every 2 overs (simple rotation)
        eligible = [b for b in bowlers if b["bowling_skill"] > 0 and b != current_bowler]
        if eligible:
            current_bowler = max(eligible, key=lambda b: b["bowling_skill"] - b.get("overs", 0) * 5)
            if "overs" not in current_bowler:
                current_bowler["overs"]   = 0
                current_bowler["wickets"] = 0
                current_bowler["runs"]    = 0

        # Ask for new strategy every 10 overs
        if (over + 1) % 10 == 0 and score["wickets"] < 10:
            strategy = prompt_strategy()

        session_runs += result["runs"] if result["outcome"] != "wicket" else 0

    return score, session_runs, session_wickets, session_overs, True


# ── Full innings ───────────────────────────────────────────────────────────────

def run_innings(batting_xi, bowling_xi, innings_num, match_state, target=None):
    """Runs a full innings across multiple days/sessions."""

    score = {"runs": 0, "wickets": 0, "overs": 0}
    day   = 1

    console.print(f"\n[bold yellow]{'═'*50}[/bold yellow]")
    console.print(f"[bold white]  INNINGS {innings_num} — {match_state['batting_team']} batting[/bold white]")
    console.print(f"[bold yellow]{'═'*50}[/bold yellow]\n")
    time.sleep(1)

    for day in range(1, MAX_DAYS + 1):
        match_state["day"] = day

        for s_idx in range(SESSIONS_PER_DAY):
            match_state["session"] = SESSION_NAMES[s_idx]

            score, s_runs, s_wkts, s_ovs, ongoing = run_session(
                batting_xi, bowling_xi, score, match_state, target
            )

            display_session_summary({
                "runs": s_runs,
                "wickets": s_wkts,
                "overs": s_ovs
            })
            time.sleep(1.5)

            # Innings over?
            if score["wickets"] >= 10:
                return score
            if target and score["runs"] >= target:
                return score

        display_day_summary(day, score)

        # Offer declaration after day 2
        if innings_num == 1 and day >= 2:
            console.print("\n[bold cyan]Do you want to declare? (y/n):[/bold cyan] ", end="")
            dec = input().strip().lower()
            if dec == "y":
                console.print(f"[bold yellow]{match_state['batting_team']} have declared![/bold yellow]")
                time.sleep(1)
                return score

        time.sleep(1)

    return score


# ── Toss ───────────────────────────────────────────────────────────────────────

def do_toss(player_team_name, ai_team_name):
    """Simulates the toss."""
    console.print("\n[bold yellow] TOSS TIME [/bold yellow]")
    console.print("Call it — [yellow]heads[/yellow] or [yellow]tails[/yellow]: ", end="")
    call = input().strip().lower()

    result = random.choice(["heads", "tails"])
    won    = call == result

    console.print(f"\nThe coin landed on [bold]{result}[/bold]!")

    if won:
        console.print(f"[bold green]You won the toss![/bold green]")
        console.print("Do you want to [yellow]bat[/yellow] or [yellow]bowl[/yellow] first? ", end="")
        choice = input().strip().lower()
        bat_first = choice == "bat"
    else:
        console.print(f"[bold red]{ai_team_name} won the toss and elected to bat.[/bold red]")
        bat_first = False

    return bat_first


# ── Main game ──────────────────────────────────────────────────────────────────

def run_match():
    """Entry point — runs the full Test match."""

    console.print("\n[bold yellow]{'═'*50}[/bold yellow]")
    console.print("[bold white] LEGENDS OF CRICKET — TEST MATCH [/bold white]")
    console.print("[bold yellow]{'═'*50}[/bold yellow]\n")

    all_names   = list(players.keys())
    player_xi   = select_team(all_names, "YOUR")
    remaining   = [n for n in all_names if n not in player_xi]
    ai_xi       = ai_select_team(remaining)

    player_name = "Your XI"
    ai_name     = "Legends XI"

    bat_first = do_toss(player_name, ai_name)

    if bat_first:
        bat1_xi, bowl1_xi = player_xi, ai_xi
        bat1_name, bowl1_name = player_name, ai_name
    else:
        bat1_xi, bowl1_xi = ai_xi, player_xi
        bat1_name, bowl1_name = ai_name, player_name

    # ── Innings 1 ──
    match_state = {
        "day": 1, "session": "Morning",
        "batting_team": bat1_name,
        "fielding_team": bowl1_name,
        "batters_at_crease": [],
        "current_bowler": None,
        "score": {"runs": 0, "wickets": 0, "overs": "0.0", "run_rate": 0.0},
        "target": None,
    }

    innings1 = run_innings(bat1_xi, bowl1_xi, 1, match_state)
    console.print(f"\n[bold]First innings: {bat1_name} — {innings1['runs']}/{innings1['wickets']}[/bold]\n")
    time.sleep(2)

    # ── Innings 2 ──
    match_state["batting_team"] = bowl1_name
    match_state["fielding_team"] = bat1_name
    target = innings1["runs"] + 1

    innings2 = run_innings(bowl1_xi, bat1_xi, 2, match_state, target=target)

    # ── Result ──
    if innings2["runs"] >= target:
        winner  = bowl1_name
        margin  = f"by {10 - innings2['wickets']} wickets"
    else:
        winner  = bat1_name
        deficit = target - innings2["runs"] - 1
        margin  = f"by {deficit} runs"

    display_match_result(f" {winner} won {margin}!")
