from __future__ import annotations
import ast
import itertools
import json
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import typer
from rich.console import Console
from rich.table import Table
import IBEXMapper as ibex

INTRO_MESSAGE = r"""
 ___ ____  _______  __    __  __    _    ____  ____  _____ ____  
|_ _| __ )| ____\ \/ /   |  \/  |  / \  |  _ \|  _ \| ____|  _ \ 
 | ||  _ \|  _|  \  /    | |\/| | / _ \ | |_) | |_) |  _| | |_) |
 | || |_) | |___ /  \    | |  | |/ ___ \|  __/|  __/| |___|  _ < 
|___|____/|_____/_/\_\___|_|  |_/_/   \_\_|   |_|   |_____|_| \_\ 
Space Research Centre · Polish Academy of Sciences
"""

console = Console()
app = typer.Typer(add_completion=False, help="IBEXMapper CLI")

mapper = ibex.getObjectInstance()
CONFIG_FILE = Path(mapper.CONFIG_FILE)
FEATURES_FILE = Path(mapper.FEATURES_FILE)

def _spinner(msg: str, done: threading.Event, interval: float = 0.1) -> None:
    for ch in itertools.cycle("|/-\\"):
        if done.is_set():
            break
        sys.stdout.write(f"\r{msg} {ch}")
        sys.stdout.flush()
        time.sleep(interval)
    sys.stdout.write("\r" + " " * (len(msg) + 2) + "\r")
    sys.stdout.flush()


def _parse_point(txt: str) -> Tuple[float, float]:
    try:
        if "," in txt and not txt.strip().startswith("("):
            txt = f"({txt})"
        lon, lat = ast.literal_eval(txt)
        lon_f, lat_f = float(lon), float(lat)
        return lon_f, lat_f
    except Exception as exc:
        raise typer.BadParameter("Expected '(lon, lat)'.") from exc


def _current_cfg() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        mapper.resetConfig()
    return json.loads(CONFIG_FILE.read_text())


def _typed_cfg(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Convert *raw* JSON values from disk to properly typed config dict."""
    mapper = ibex.getObjectInstance()
    return mapper.formatConfigDatastructures(raw)

    # return ibex.createNewConfig(raw)


def _save_cfg(cfg: Dict[str, Any]) -> None:
    ibex.setDefaultConfig(cfg)

@app.command("generate", help="Generate map from data file (spinner always on).")
def cmd_generate(
    link: Path = typer.Argument(..., exists=True, readable=True),
    use_saved_config: bool = typer.Option(True, "--config/--no-config"),
):
    cfg: Optional[Dict[str, Any]] = _typed_cfg(_current_cfg()) if use_saved_config else None
    done = threading.Event()
    t = threading.Thread(target=_spinner, args=("GENERATING MAP", done), daemon=True)
    t.start()
    try:
        ibex.generateMapFromLink(str(link), cfg)
    finally:
        done.set()
        t.join()
    console.print("[bold green]Map generated.[/bold green]")


@app.command("add-point")
def cmd_add_point(
    name: str = typer.Argument(...),
    coords: str = typer.Argument(...),
    color: str = typer.Option("black", "--color"),
):
    lon, lat = _parse_point(coords)
    ibex.addPoint(name, (lon, lat), color)
    console.print(f"[green]Added '{name}'.[/green]")


@app.command("remove-point")
def cmd_remove_point(name: str):
    ibex.removePoint(name)
    console.print(f"[yellow]Removed '{name}'.[/yellow]")


@app.command("list-points")
def cmd_list_points():
    if not FEATURES_FILE.exists():
        console.print("[italic]No points stored.[/italic]")
        return
    pts = json.loads(FEATURES_FILE.read_text()).get("points", [])
    if not pts:
        console.print("[italic]No points stored.[/italic]")
        return
    tbl = Table(title="Stored points")
    tbl.add_column("Name", style="bold")
    tbl.add_column("Lon")
    tbl.add_column("Lat")
    tbl.add_column("Color")
    for p in pts:
        lon, lat = ast.literal_eval(p["coordinates"])
        tbl.add_row(p["name"], str(lon), str(lat), p.get("color", "black"))
    console.print(tbl)


@app.command("remove-all-points")
def cmd_remove_all_points(yes: bool = typer.Option(False, "--yes", "-y")):
    if not yes and not typer.confirm("DELETE ALL points?"):
        raise typer.Exit()
    ibex.removeAllPoints(); console.print("[yellow]All points removed.[/yellow]")


@app.command("config-show")
def cmd_config_show():
    cfg = _current_cfg(); tbl = Table(title="Configuration (raw JSON)")
    for k, v in cfg.items(): tbl.add_row(k, str(v))
    console.print(tbl)


@app.command("config-set")
def cmd_config_set(
    map_accuracy: Optional[int] = typer.Option(None),
    max_l_to_cache: Optional[int] = typer.Option(None),
    rotate: Optional[bool] = typer.Option(None, "--rotate/--no-rotate"),
    central_point: Optional[str] = typer.Option(None),
    meridian_point: Optional[str] = typer.Option(None),
    allow_negative_values: Optional[bool] = typer.Option(None, "--allow-neg/--disallow-neg"),
):
    upd: Dict[str, Any] = {}
    if map_accuracy is not None: upd["map_accuracy"] = map_accuracy
    if max_l_to_cache is not None: upd["max_l_to_cache"] = max_l_to_cache
    if rotate is not None: upd["rotate"] = rotate
    if central_point is not None: upd["central_point"] = central_point
    if meridian_point is not None: upd["meridian_point"] = meridian_point
    if allow_negative_values is not None: upd["allow_negative_values"] = allow_negative_values
    if not upd:
        console.print("[red]Nothing to update.[/red]"); raise typer.Exit()
    new_cfg = ibex.createNewConfig(upd); _save_cfg(new_cfg)
    console.print("[green]Config updated.[/green]")


@app.command("config-reset")
def cmd_config_reset(yes: bool = typer.Option(False, "--yes", "-y")):
    if not yes and not typer.confirm("Reset configuration to defaults?"):
        raise typer.Exit()
    ibex.resetConfigToDefaultConfig()
    console.print("[yellow]Configuration reset.[/yellow]")


_MENU = """
[bold green]IBEX Mapper[/bold green]

1 Generate map
2 Add point
3 Remove point
4 List points
5 Remove all points
6 Show configuration
7 Set configuration fields
8 Reset configuration
9 Exit
"""

def _prompt_point() -> Tuple[str, float, float, str]:
    n = typer.prompt("Point name")
    c = typer.prompt("Coordinates (lon, lat)")
    col = typer.prompt("Color", default="black")
    lon, lat = _parse_point(c)
    return n, lon, lat, col


def _menu_loop() -> None:
    print(INTRO_MESSAGE)
    while True:
        console.clear()
        console.print(_MENU)
        choice = typer.prompt("Select option", type=int)
        try:
            if choice == 1:
                p = typer.prompt("Path to data file", prompt_suffix=" -> ")
                cfg_on = typer.confirm("Use saved configuration?", default=True)
                cmd_generate(Path(p), cfg_on)
            elif choice == 2:
                n, lon, lat, col = _prompt_point()
                ibex.addPoint(n, (lon, lat), col)
                console.print(f"[green]Added '{n}'.[/green]")
            elif choice == 3:
                n = typer.prompt("Name to remove")
                ibex.removePoint(n)
                console.print(f"[yellow]Removed '{n}'.[/yellow]")
            elif choice == 4:
                cmd_list_points()
            elif choice == 5:
                if typer.confirm("DELETE ALL points?", default=False): ibex.removeAllPoints()
                console.print("[yellow]All points removed.[/yellow]")
            elif choice == 6:
                cmd_config_show()
            elif choice == 7:
                console.print("Leave blank to keep value.")
                ma = typer.prompt("map_accuracy", default="")
                ml = typer.prompt("max_l_to_cache", default="")
                rot = typer.prompt("rotate (true/false)", default="")
                cp = typer.prompt("central_point", default="")
                mp = typer.prompt("meridian_point", default="")
                an = typer.prompt("allow_negative_values (true/false)", default="")
                upd: Dict[str, Any] = {}
                if ma: upd["map_accuracy"] = int(ma)
                if ml: upd["max_l_to_cache"] = int(ml)
                if rot.lower() in {"true", "false"}: upd["rotate"] = rot.lower() == "true"
                if cp: upd["central_point"] = cp
                if mp: upd["meridian_point"] = mp
                if an.lower() in {"true", "false"}: upd["allow_negative_values"] = an.lower() == "true"
                if upd:
                    _save_cfg(ibex.createNewConfig(upd))
                    console.print("[green]Config updated.[/green]")
                else:
                    console.print("[italic]Nothing changed.[/italic]")
            elif choice == 8:
                if typer.confirm("Reset configuration to defaults?", default=False): ibex.resetConfigToDefaultConfig()
                console.print("[yellow]Configuration reset.[/yellow]")
            elif choice == 9:
                console.print("[cyan]Goodbye[/cyan]")
                break
            else:
                console.print("[red]Invalid choice.[/red]")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
        typer.echo()
        typer.pause("Press any key to continue…")


@app.command("menu", help="Start interactive menu")
def cmd_menu():
    _menu_loop()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _menu_loop()
    else:
        app()
