# ball.py

import random

def simulate_ball(batsman, bowler, strategy):
    """
    Simulates a single ball outcome based on:
    - batsman's attack/defense stats
    - bowler's bowling_skill
    - player's chosen strategy (aggressive/balanced/defensive)
    """

    # Strategy modifiers
    strategy_mods = {
        "aggressive": {"attack_boost": 15, "defense_penalty": 20, "wicket_boost": 10},
        "balanced":   {"attack_boost": 0,  "defense_penalty": 0,  "wicket_boost": 0},
        "defensive":  {"attack_boost": -15,"defense_penalty": -15, "wicket_boost": -10},
    }

    mod = strategy_mods.get(strategy, strategy_mods["balanced"])

    # Effective stats after strategy applied
    effective_attack  = batsman["attack"]  + mod["attack_boost"]
    effective_defense = batsman["defense"] - mod["defense_penalty"]
    effective_bowl    = bowler["bowling_skill"]

    # Wicket probability
    # Higher bowling skill + aggressive batting = more risk
    wicket_chance = max(5, min(40,
        (effective_bowl - effective_defense) / 2 + mod["wicket_boost"]
    ))

    # Roll for wicket first
    if random.uniform(0, 100) < wicket_chance:
        return {"outcome": "wicket", "runs": 0, "commentary": get_commentary("wicket", batsman, bowler)}

    # Otherwise, determine runs scored
    # Higher attack vs lower bowling = more runs likely
    run_weight = max(10, effective_attack - effective_bowl / 2)

    outcomes = {
        0: max(10, 50 - run_weight),   # dot ball
        1: 20,
        2: 15,
        3: 5,
        4: max(5, run_weight / 3),     # boundary
        6: max(2, run_weight / 5),     # six
    }

    runs = random.choices(
        list(outcomes.keys()),
        weights=list(outcomes.values())
    )[0]

    return {
        "outcome": "runs",
        "runs": runs,
        "commentary": get_commentary("runs", batsman, bowler, runs)
    }


def get_commentary(event, batsman, bowler, runs=0):
    """Returns a flavourful commentary line."""

    wicket_lines = [
        f"OUT! {bowler['name']} strikes! {batsman['name']} has to walk back.",
        f"What a delivery! {batsman['name']} is clean bowled by {bowler['name']}!",
        f"Gone! {bowler['name']} gets the big wicket of {batsman['name']}!",
        f"That's out! {batsman['name']} couldn't handle that one from {bowler['name']}.",
    ]

    run_lines = {
        0: [
            f"Dot ball. {bowler['name']} is keeping it tight.",
            f"Excellent line and length from {bowler['name']}. Nothing doing!",
            f"{batsman['name']} plays it straight to the fielder. No run.",
        ],
        1: [f"Nudged away for a single by {batsman['name']}."],
        2: [f"Good running! {batsman['name']} turns it for two."],
        3: [f"Three runs! {batsman['name']} finds the gap."],
        4: [
            f"FOUR! {batsman['name']} drives it beautifully through the covers!",
            f"FOUR! That raced away to the boundary off {batsman['name']}'s bat!",
            f"Cracking shot! {batsman['name']} finds the fence!",
        ],
        6: [
            f"SIX! {batsman['name']} launches it into the stands!",
            f"MASSIVE SIX! {batsman['name']} takes on {bowler['name']} and wins!",
            f"That's gone all the way! {batsman['name']} hits it out of the ground!",
        ],
    }

    if event == "wicket":
        return random.choice(wicket_lines)
    else:
        lines = run_lines.get(runs, [f"{runs} runs scored."])
        return random.choice(lines)
