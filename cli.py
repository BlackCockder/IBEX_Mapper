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
import traceback
from rich.traceback import install

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
SESSION_CFG: dict | None = None

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


def _current_cfg() -> dict:
    return ibex.getDefaultConfig()


    # return ibex.createNewConfig(raw)


def _save_cfg(cfg: dict) -> None:
    ibex.setDefaultConfig(cfg)

@app.command("generate", help="Generate map from data file (spinner always on).")
def cmd_generate(
    link: Path = typer.Argument(..., exists=True, readable=True),
    use_saved_config: bool = typer.Option(True, "--config/--no-config"),
):
    cfg: Optional[Dict[str, Any]] = _current_cfg() if use_saved_config else None
    print(cfg)
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
    if allow_negative_values is not None: upd["show_negative_values"] = allow_negative_values
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
[bold green]IBEX MAPPER[/bold green]  

1 Generate map  
2 Add point  
3 Remove point  
4 List points  
5 Remove all points
6 Add circle # not working
7 Remove circle # not working
8 List circles # not working
9 Remove all circles # not working 
10 Add text # not working
11 Remove text # not working
12 List all text # not working
13 Remove all texts # not working
14 Change heatmap color # not working
15 Change heatmap scale # not working
16 Clear heatmap scale # not working
17 Show configuration  
18 Set configuration fields  
19 Reset configuration
20 Set selected configuration as default  
21 Exit  
"""

def _prompt_point() -> Tuple[str, float, float, str]:
    n = typer.prompt("Point name")
    c = typer.prompt("Coordinates (lon, lat)")
    col = typer.prompt("Color", default="green")
    lon, lat = _parse_point(c)
    return n, lon, lat, col


def _menu_loop() -> None:
    console.print(f"[purple]{INTRO_MESSAGE}[/purple]")
    while True:
        console.clear()
        console.print(_MENU)
        choice = typer.prompt("Select option", type=int)
        try:
            if choice == 1: # generate map
                # generateMapFromLink i InputFolder / totalnie to zmiany
                p = typer.prompt("Path to data file", prompt_suffix=" -> ")
                use_saved = typer.confirm("Use saved configuration?", default=True)
                cfg = SESSION_CFG if use_saved and SESSION_CFG is not None else ibex.getDefaultConfig()
                done = threading.Event()
                t = threading.Thread(target=_spinner, args=("GENERATING MAP", done), daemon=True)
                t.start()
                try:
                    ibex.generateMapFromLink(p, cfg)
                finally:
                    done.set()
                    t.join()
                console.print("[bold green]Map generated.[/bold green]")
                # cmd_generate(Path(p), use_saved)
            elif choice == 2: # add point
                # git
                n, lon, lat, col = _prompt_point()
                ibex.addPoint(n, (lon, lat), col)
                console.print(f"[green]Added '{n}'.[/green]")
            elif choice == 3: # remove point
                # git
                n = typer.prompt("Name to remove:")
                ibex.removePoint(n)
                console.print(f"[yellow]Removed '{n}'.[/yellow]")
            elif choice == 4: # list points
                # TODO: dokonczyc
                cmd_list_points()
            elif choice == 5: # remove all points
                # git
                if typer.confirm("DELETE ALL points?", default=False):
                    ibex.removeAllPoints()
                console.print("[yellow]All points removed.[/yellow]")
            elif choice == 6: # add circle
                # TODO: dokonczyc
                n, lon, lat, col = _prompt_point()
                ibex.addCircle(n, (lon, lat), col)
                console.print(f"[green]Added circle '{n}'.[/green]")
            elif choice == 7: # remove circle
                n = typer.prompt("Name of circle to remove")
                ibex.removeCircle(n)
                console.print(f"[yellow]Removed circle '{n}'.[/yellow]")
            elif choice == 8: # list circles
                # TODO: dokonczyc
                circles = ibex.listCircles()
                if not circles:
                    console.print("[italic]No circles stored.[/italic]")
                    continue
                tbl = Table(title="Stored circles")
                tbl.add_column("Name", style="bold")
                tbl.add_column("Lon")
                tbl.add_column("Lat")
                tbl.add_column("Color")
                for c in circles:
                    lon, lat = ast.literal_eval(c["coordinates"])
                    tbl.add_row(c["name"], str(lon), str(lat), c.get("color", "black"))
                console.print(tbl)
            elif choice == 9: # remove all circles
                # git
                if typer.confirm("DELETE ALL circles?", default=False):
                    ibex.removeAllCircles()
                console.print("[yellow]All circles removed.[/yellow]")
            elif choice == 10: # add text
                # TODO: dokonczyc
                n = typer.prompt("Text name")
                c = typer.prompt("Coordinates (lon, lat)")
                col = typer.prompt("Color", default="black")
                text = typer.prompt("Text content")
                lon, lat = _parse_point(c)
                ibex.addMapText(n, (lon, lat), text, col)
                console.print(f"[green]Added text '{n}'.[/green]")
            elif choice == 11: # remove text
                # git
                n = typer.prompt("Name of text to remove")
                ibex.removeMapText(n)
                console.print(f"[yellow]Removed text '{n}'.[/yellow]")
            elif choice == 12: # list all texts
                texts = ibex.listTexts()
                if not texts:
                    console.print("[italic]No texts stored.[/italic]")
                    continue
                tbl = Table(title="Stored texts")
                tbl.add_column("Name", style="bold")
                tbl.add_column("Lon")
                tbl.add_column("Lat")
                tbl.add_column("Color")
                tbl.add_column("Content")
                for t in texts:
                    lon, lat = ast.literal_eval(t["coordinates"])
                    tbl.add_row(t["name"], str(lon), str(lat), t.get("color", "black"), t["content"])
                console.print(tbl)
            elif choice == 13: # remove all texts
                # git
                if typer.confirm("DELETE ALL texts?", default=False):
                    ibex.removeAllMapText()
                console.print("[yellow]All texts removed.[/yellow]")
            elif choice == 14: # change heatmap color
                # git
                color = typer.prompt("New heatmap color", default="blue")
                ibex.selectHeatmapColorPalette(color)
                console.print(f"[green]Heatmap color set to '{color}'.[/green]")
            elif choice == 15: # change heatmap scale
                color = typer.prompt("New heatmap scale", default="magma")
                ibex.changeHeatmapScale(color)
                console.print(f"[green]Heatmap scale set to '{color}'.[/green]")
            elif choice == 16: # clear heatmap scale
                ibex.resetHeatmapScaleToDefault()
            elif choice == 17: # show configuration
                # TODO: dokonczyc
                cmd_config_show()
            elif choice == 18: # set configuration fields
                console.print("Leave blank to keep value.")
                ma = typer.prompt("map_accuracy", default="")
                ml = typer.prompt("max_l_to_cache", default="")
                rot = typer.prompt("rotate (true/false)", default="")
                cp = typer.prompt("central_point", default="")
                mp = typer.prompt("meridian_point", default="")
                an = typer.prompt("show_negative_values (true/false)", default="")
                upd: dict = {"map_accuracy": ma,
                             "max_l_to_cache": ml,
                             "rotate": rot,
                             "central_point": cp,
                             "meridian_point": mp,
                             "show_negative_values": an
                             }
                formatted_cfg = mapper.handler.formatConfigToPythonDatastructures(upd)
                # if ma: upd["map_accuracy"] = int(ma)
                # if ml: upd["max_l_to_cache"] = int(ml)
                # if rot.lower() in {"true", "false"}: upd["rotate"] = rot.lower() == "true"
                # if cp: upd["central_point"] = cp
                # if mp: upd["meridian_point"] = mp
                # if an.lower() in {"true", "false"}:
                formatted_cfg["show_negative_values"] = an.lower() == "true"
                if upd:
                    SESSION_CFG = ibex.createNewConfig(formatted_cfg)
                    console.print("[green]Config updated until exiting the program.[/green]")
                else:
                    console.print("[italic]Nothing changed.[/italic]")
            elif choice == 19: # reset configuration
                if typer.confirm("Reset configuration to defaults?", default=False):
                    ibex.resetConfigToDefaultConfig()
                console.print("[yellow]Configuration reset.[/yellow]")
            elif choice == 20: # set selected configuration as default
                ibex.setDefaultConfig() # upd
            elif choice == 21: # exit
                console.print("[cyan]Goodbye[/cyan]")
                break
            else:
                console.print("[red]Invalid choice.[/red]")
        except Exception as e:
            # console.print(f"[red]Error:[/red] {e}")
            # console.print("[red]An unexpected error occurred:[/red]")
            print(e)
            install(show_locals=True)
            raise
        typer.echo()
        typer.pause("Press any key to continue...")



@app.command("menu", help="Start interactive menu")
def cmd_menu():
    _menu_loop()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _menu_loop()
    else:
        app()

# def main() -> None:
#     mapper = ib.getObjectInstance()
#     mapper.generateMapFromLink(link) # "t2010_02.txt"
#     np.set_printoptions(precision=8, suppress=True, floatmode='fixed')
#     config = mapper.def_config
#     initial_center = np.array([0, 0])
#     target_center = config["location_of_central_point"]
#     meridian_vector = config["meridian_point"]
#     print("-------------------------------------------------------")
#     print("Vectors in degrees:")
#     print(f"Central vector: {initial_center}")
#     print(f"Target center vector: {target_center}")
#     print(f"Meridian vector: {meridian_vector}")
#     initial_center_in_cartesian = mapper.configurator.convertSphericalToCartesianForPoints(initial_center)
#     target_center_in_cartesian = mapper.configurator.convertSphericalToCartesianForPoints(target_center)
#     meridian_vector_in_cartesian = mapper.configurator.convertSphericalToCartesianForPoints(meridian_vector)
#     print("-------------------------------------------------------")
#     print("Vectors in cartesian coordinates: ")
#     print(f"Central vector: {initial_center_in_cartesian}")
#     print(f"Target center vector: {target_center_in_cartesian}")
#     print(f"Meridian vector: {meridian_vector_in_cartesian}")
#     central_rotation = mapper.configurator.buildCenteringRotation(target_center)
#     meridian_rotation = mapper.configurator.buildMeridianRotation(meridian_vector, central_rotation)
#     print("-------------------------------------------------------")
#     print("Rotations: ")
#     print(f"Central rotation: \n{central_rotation}")
#     print(f"Meridian rotation: \n{meridian_rotation}")
#     initial_center_in_cartesian_after_1st_rotation = central_rotation @ initial_center_in_cartesian
#     target_center_in_cartesian_after_1st_rotation = central_rotation @ target_center_in_cartesian
#     meridian_vector_in_cartesian_after_1st_rotation = central_rotation @ meridian_vector_in_cartesian
#     print("-------------------------------------------------------")
#     print("Vectors after first rotation in spherical coordinates: ")
#     print(f"Initial central vector: {np.rad2deg(np.array(mapper.calculator
#       .convertCartesianToSpherical(initial_center_in_cartesian_after_1st_rotation[0],
#                                    initial_center_in_cartesian_after_1st_rotation[1],
#                                    initial_center_in_cartesian_after_1st_rotation[2])))}")
#     print(f"Target center vector: {np.rad2deg(np.array(mapper.calculator
#       .convertCartesianToSpherical(target_center_in_cartesian_after_1st_rotation[0],
#                                    target_center_in_cartesian_after_1st_rotation[1],
#                                    target_center_in_cartesian_after_1st_rotation[2])))}")
#     print(f"Meridian vector: {np.rad2deg(np.array(mapper.calculator
#       .convertCartesianToSpherical(meridian_vector_in_cartesian_after_1st_rotation[0],
#                                    meridian_vector_in_cartesian_after_1st_rotation[1],
#                                    meridian_vector_in_cartesian_after_1st_rotation[2])))}")
#     print("-------------------------------------------------------")
#     print("Vectors after first rotation in cartesian coordinates: ")
#     print(f"Central vector: {initial_center_in_cartesian_after_1st_rotation}")
#     print(f"Target center vector: {target_center_in_cartesian_after_1st_rotation}")
#     print(f"Meridian vector: {meridian_vector_in_cartesian_after_1st_rotation}")
#     initial_center_in_cartesian_after_2nd_rotation = meridian_rotation @ initial_center_in_cartesian_after_1st_rotation
#     target_center_in_cartesian_after_2nd_rotation = meridian_rotation @ target_center_in_cartesian_after_1st_rotation
#     meridian_vector_in_cartesian_after_2nd_rotation = meridian_rotation @ meridian_vector_in_cartesian_after_1st_rotation
#     print("-------------------------------------------------------")
#     print("Vectors after second rotation in spherical coordinates: ")
#     print(f"Initial central vector: {np.rad2deg(np.array(mapper.calculator
#                                                      .convertCartesianToSpherical(initial_center_in_cartesian_after_2nd_rotation[0],
#                                                                                   initial_center_in_cartesian_after_2nd_rotation[1],
#                                                                                   initial_center_in_cartesian_after_2nd_rotation[2]))) }")
#     print(f"Target center vector: {np.rad2deg(np.array(mapper.calculator
#                                     .convertCartesianToSpherical(target_center_in_cartesian_after_2nd_rotation[0],
#                                                                  target_center_in_cartesian_after_2nd_rotation[1],
#                                                                  target_center_in_cartesian_after_2nd_rotation[2])))}")
#     print(f"Meridian vector: {np.rad2deg(np.array(mapper.calculator
#                                .convertCartesianToSpherical(meridian_vector_in_cartesian_after_2nd_rotation[0],
#                                                             meridian_vector_in_cartesian_after_2nd_rotation[1],
#                                                             meridian_vector_in_cartesian_after_2nd_rotation[2])))}")
#     print("-------------------------------------------------------")
#     print("Vectors after second rotation in cartesian coordinates: ")
#     print(f"Central vector: {initial_center_in_cartesian_after_2nd_rotation}")
#     print(f"Target center vector: {target_center_in_cartesian_after_2nd_rotation}")
#     print(f"Meridian vector: {meridian_vector_in_cartesian_after_2nd_rotation}")
#     combined_rotation = meridian_rotation @ central_rotation
#     print("-------------------------------------------------------")
#     print(f"Combined rotation: \n{combined_rotation}")
#     initial_center_in_cartesian_after_combined_rotation = combined_rotation @ initial_center_in_cartesian
#     target_center_in_cartesian_after_combined_rotation = combined_rotation @ target_center_in_cartesian
#     meridian_vector_in_cartesian_after_combined_rotation = combined_rotation @ meridian_vector_in_cartesian
#     print("-------------------------------------------------------")
#     print("Vectors after combined rotation in spherical coordinates: ")
#     print(f"Initial central vector: {np.rad2deg(np.array(mapper.calculator
#                                                      .convertCartesianToSpherical(initial_center_in_cartesian_after_combined_rotation[0],
#                                                                                   initial_center_in_cartesian_after_combined_rotation[1],
#                                                                                   initial_center_in_cartesian_after_combined_rotation[2]))) }")
#     print(f"Target center vector: {np.rad2deg(np.array(mapper.calculator
#                                                    .convertCartesianToSpherical(target_center_in_cartesian_after_combined_rotation[0],
#                                                                                 target_center_in_cartesian_after_combined_rotation[1],
#                                                                                 target_center_in_cartesian_after_combined_rotation[2])))}")
#     print(f"Meridian vector: {np.rad2deg(np.array(mapper.calculator
#                                               .convertCartesianToSpherical(meridian_vector_in_cartesian_after_combined_rotation[0],
#                                                                            meridian_vector_in_cartesian_after_combined_rotation[1],
#                                                                            meridian_vector_in_cartesian_after_combined_rotation[2])))}")
#     print("-------------------------------------------------------")
#     print("Vectors after combined rotation in cartesian coordinates: ")
#     print(f"Central vector: {initial_center_in_cartesian_after_combined_rotation}")
#     print(f"Target center vector: {target_center_in_cartesian_after_combined_rotation}")
#     print(f"Meridian vector: {meridian_vector_in_cartesian_after_combined_rotation}")