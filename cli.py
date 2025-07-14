from __future__ import annotations
import itertools
import shlex
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import json
import os
import ast
import numpy as np
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# ────────────────────────────────────────────────────────────────────────────────
#  Import your real library here
#  (the MockMapper below is only for standalone demonstration)
# ────────────────────────────────────────────────────────────────────────────────
try:
    import IBEXMapper as ibex                       # production path
except ModuleNotFoundError:                         # dev / test fallback
    from mock_mapper import MockMapper as ibex      # noqa: F401,E402

# ────────────────────────────────────────────────────────────────────────────────
INTRO_MESSAGE = r"""
 ___ ____  _______  __    __  __    _    ____  ____  _____ ____  
|_ _| __ )| ____\ \/ /   |  \/  |  / \  |  _ \|  _ \| ____|  _ \ 
 | ||  _ \|  _|  \  /    | |\/| | / _ \ | |_) | |_) |  _| | |_) |
 | || |_) | |___ /  \    | |  | |/ ___ \|  __/|  __/| |___|  _ < 
|___|____/|_____/_/\_\___|_|  |_/_/   \_\_|   |_|   |_____|_| \_\ 
                 Space Research Centre · Polish Academy of Sciences
"""

APP_DIR = Path(__file__).parent
CONFIG_DIR = APP_DIR / "config"
POINTS_FILE = APP_DIR / "map_features" / "map_features.json"
CONFIG_FILE = CONFIG_DIR / "config.json"

console = Console()
app = typer.Typer(no_args_is_help=False, help="IBEX Mapper CLI – generate and manage IBEX maps.")


# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────
def _spinner(label: str, stop_event: threading.Event, delay: float = .1) -> None:
    for ch in itertools.cycle("|/-\\"):
        if stop_event.is_set():
            break
        sys.stdout.write(f"\r{label} {ch}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\r" + " " * (len(label) + 2) + "\r")
    sys.stdout.flush()


def _run_map_generation(link: str, show_spinner: bool, cfg: Optional[Dict[str, Any]] = None) -> None:
    stop = threading.Event()
    if show_spinner:
        threading.Thread(target=_spinner, args=("GENERATING MAP", stop), daemon=True).start()

    mapper = ibex.getObjectInstance()
    cfg = mapper.formatConfigDatastructures(cfg) if cfg else None
    mapper.generateMapFromLink(link, cfg)

    if show_spinner:
        stop.set()
    rprint("[green]MAP GENERATED[/green]")


def _load_cfg() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        ibex.getObjectInstance().resetConfig()
    return json.loads(CONFIG_FILE.read_text())


def _save_cfg(cfg: Dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=4, default=str))


def _parse_point(val: str) -> Tuple[float, float]:
    try:
        pt = ast.literal_eval(val)
        if (
            isinstance(pt, tuple)
            and len(pt) == 2
            and all(isinstance(n, (int, float)) for n in pt)
        ):
            return pt  # type: ignore[return-value]
        raise ValueError
    except Exception:
        raise typer.BadParameter("Expected format: '(lon, lat)', e.g. '(100, -30)'.")


# ────────────────────────────────────────────────────────────────────────────────
# CLI commands
# ────────────────────────────────────────────────────────────────────────────────
@app.command()
def generate(
    file_path: Path = typer.Option(
        ..., "--file", "-f", prompt="Path to the IBEX data file",
        help="Text file with IBEX spherical-harmonics coefficients",
        exists=True, readable=True, dir_okay=False
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress banner and timing info."),
    spinner: bool = typer.Option(True, "--spinner/--no-spinner", help="Show animated progress bar."),
    use_config: bool = typer.Option(False, "--use-config", "-c", help="Use saved configuration file."),
):
    """Generate a map from an IBEX data file."""
    if not quiet:
        console.print(INTRO_MESSAGE)
    t0 = time.time()
    cfg = _load_cfg() if use_config else None
    _run_map_generation(str(file_path), show_spinner=spinner and not quiet, cfg=cfg)
    if not quiet:
        console.print(f"[bold green]Completed in {time.time() - t0:.2f} s[/bold green]")


@app.command("config-show")
def config_show() -> None:
    """Display current configuration."""
    cfg = _load_cfg()
    tbl = Table(title="IBEX Mapper Configuration")
    tbl.add_column("Key", style="cyan")
    tbl.add_column("Value", style="magenta")
    tbl.add_column("Type", style="yellow")
    for k, v in cfg.items():
        tbl.add_row(k, str(v), type(v).__name__)
    console.print(tbl)


@app.command("config-set")
def config_set(
    map_accuracy: Optional[int] = typer.Option(None, prompt=False),
    max_l_to_cache: Optional[int] = typer.Option(None, prompt=False),
    rotate: Optional[bool] = typer.Option(None, prompt=False),
    central_point: Optional[str] = typer.Option(None, prompt=False),
    meridian_point: Optional[str] = typer.Option(None, prompt=False),
    allow_negative_values: Optional[bool] = typer.Option(None, prompt=False),
):
    """Update selected configuration keys."""
    cfg = _load_cfg()
    updates: Dict[str, Any] = {}
    if map_accuracy is not None:
        updates["map_accuracy"] = map_accuracy
    if max_l_to_cache is not None:
        updates["max_l_to_cache"] = max_l_to_cache
    if rotate is not None:
        updates["rotate"] = rotate
    if allow_negative_values is not None:
        updates["allow_negative_values"] = allow_negative_values
    if central_point:
        updates["central_point"] = _parse_point(central_point)
    if meridian_point:
        updates["meridian_point"] = _parse_point(meridian_point)

    if not updates:
        rprint("[yellow]Nothing to update.[/yellow]")
        raise typer.Exit()

    cfg.update(updates)
    _save_cfg(cfg)
    rprint("[green]Configuration updated.[/green]")
    config_show()


@app.command("config-reset")
def config_reset() -> None:
    """Reset configuration to factory defaults."""
    ibex.getObjectInstance().resetConfig()
    rprint("[green]Configuration reset.[/green]")


@app.command("add-point")
def add_point(
    name: str = typer.Option(..., prompt="Point name"),
    coordinates: str = typer.Option(..., prompt="Coordinates (lon, lat)"),
    color: str = typer.Option(..., prompt="Point colour"),
):
    """Add a new point that will later be plotted on the map."""
    pt = _parse_point(coordinates)
    ibex.getObjectInstance().addPoint(name, pt, color)
    rprint(f"[green]Point '{name}' added: {pt}, colour {color}.[/green]")


@app.command("list-points")
def list_points() -> None:
    """Show all stored points."""
    if not POINTS_FILE.exists():
        rprint("[yellow]No points defined.[/yellow]")
        raise typer.Exit()

    data = json.loads(POINTS_FILE.read_text())
    points = data.get("points", [])
    if not points:
        rprint("[yellow]No points defined.[/yellow]")
        raise typer.Exit()

    tbl = Table(title="Defined Map Points")
    tbl.add_column("Name", style="cyan")
    tbl.add_column("Coordinates", style="green")
    tbl.add_column("Colour", style="yellow")
    for p in points:
        tbl.add_row(p["name"], p["coordinates"], p["color"])
    console.print(tbl)


@app.command("remove-point")
def remove_point(name: str = typer.Argument(..., help="Name of the point to delete.")) -> None:
    """Delete a single point."""
    ibex.getObjectInstance().removePoint(name)
    rprint(f"[green]Point '{name}' deleted.[/green]")


@app.command("remove-all-points")
def remove_all_points() -> None:
    """Delete *all* stored points."""
    ibex.getObjectInstance().removeAllPoints()
    rprint("[green]All points wiped.[/green]")


# ────────────────────────────────────────────────────────────────────────────────
# Interactive mode (REPL)
# ────────────────────────────────────────────────────────────────────────────────
def _interactive_shell() -> None:
    console.print(INTRO_MESSAGE)
    console.print("[bold cyan]Type a command, 'help', or 'exit'.[/bold cyan]")
    while True:
        try:
            line = input("IBEX> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            break
        if line.lower() == "help":
            console.print(app.get_help(rich_markup_mode="rich"))
            continue
        try:
            app(shlex.split(line), standalone_mode=False)
        except SystemExit as exc:
            # Click/Typer converts every successful run into SystemExit(0)
            if exc.code not in (0, None):
                rprint(f"[red]Command aborted (exit code {exc.code}).[/red]")
        except Exception as exc:         # noqa: BLE001
            rprint(f"[red]Error:[/red] {exc}")


# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # run as a normal CLI
        app()
    else:
        # no extra args → REPL
        _interactive_shell()
