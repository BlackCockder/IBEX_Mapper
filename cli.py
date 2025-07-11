from __future__ import annotations
import time
import IBEXMapper as ib
import argparse
import sys
import itertools
import threading
import numpy as np

INTRO_MESSAGE = r"""
 ___ ____  _______  __    __  __    _    ____  ____  _____ ____  
|_ _| __ )| ____\ \/ /   |  \/  |  / \  |  _ \|  _ \| ____|  _ \ 
 | ||  _ \|  _|  \  /    | |\/| | / _ \ | |_) | |_) |  _| | |_) |
 | || |_) | |___ /  \    | |  | |/ ___ \|  __/|  __/| |___|  _ < 
|___|____/|_____/_/\_\___|_|  |_/_/   \_\_|   |_|   |_____|_| \_\ 
                 Space Research Centre Polish Academy of Sciences
"""


def _spinner(text: str, stop_event: threading.Event, interval: float = 0.1) -> None:
    for ch in itertools.cycle("|/-\\"):
        if stop_event.is_set():
            break
        sys.stdout.write(f"\r{text} {ch}")
        sys.stdout.flush()
        time.sleep(interval)
    # Clear the line before exiting
    sys.stdout.write("\r" + " " * (len(text) + 2) + "\r")
    sys.stdout.flush()

def run(link: str, show_spinner: bool) -> None:
    stop = threading.Event()
    if show_spinner:
        thread = threading.Thread(
            target=_spinner,
            args=("GENERATING MAP", stop),
            daemon=True,
        )
        thread.start()

    mapper = ib.getObjectInstance()
    mapper.addPoint("Testing point 1", (100, 30), "blue")
    mapper.addPoint("Testing point 2", (-100, 30), "red")
    mapper.addPoint("Testing point 3", (100, -30), "green")
    mapper.addPoint("Testing point 4", (-100, -30), "black")
    mapper.generateMapFromLink(link)

    if show_spinner:
        stop.set()
        thread.join()
        print("MAP GENERATED")

# args.link = "t2010_02.txt"

# def run(link) -> None:
#     mapper = ib.getObjectInstance()
#     mapper.generateMapFromLink(link) # "t2010_02.txt"
    # np.set_printoptions(precision=8, suppress=True, floatmode='fixed')
    # config = mapper.def_config
    # initial_center = np.array([0, 0])
    # target_center = config["location_of_central_point"]
    # meridian_vector = config["meridian_point"]
    # print("-------------------------------------------------------")
    # print("Vectors in degrees:")
    # print(f"Central vector: {initial_center}")
    # print(f"Target center vector: {target_center}")
    # print(f"Meridian vector: {meridian_vector}")
    # initial_center_in_cartesian = mapper.configurator.convertSphericalToCartesianForPoints(initial_center)
    # target_center_in_cartesian = mapper.configurator.convertSphericalToCartesianForPoints(target_center)
    # meridian_vector_in_cartesian = mapper.configurator.convertSphericalToCartesianForPoints(meridian_vector)
    # print("-------------------------------------------------------")
    # print("Vectors in cartesian coordinates: ")
    # print(f"Central vector: {initial_center_in_cartesian}")
    # print(f"Target center vector: {target_center_in_cartesian}")
    # print(f"Meridian vector: {meridian_vector_in_cartesian}")
    # central_rotation = mapper.configurator.buildCenteringRotation(target_center)
    # meridian_rotation = mapper.configurator.buildMeridianRotation(meridian_vector, central_rotation)
    # print("-------------------------------------------------------")
    # print("Rotations: ")
    # print(f"Central rotation: \n{central_rotation}")
    # print(f"Meridian rotation: \n{meridian_rotation}")
    # initial_center_in_cartesian_after_1st_rotation = central_rotation @ initial_center_in_cartesian
    # target_center_in_cartesian_after_1st_rotation = central_rotation @ target_center_in_cartesian
    # meridian_vector_in_cartesian_after_1st_rotation = central_rotation @ meridian_vector_in_cartesian
    # print("-------------------------------------------------------")
    # print("Vectors after first rotation in spherical coordinates: ")
    # print(f"Initial central vector: {np.rad2deg(np.array(mapper.calculator
    #       .convertCartesianToSpherical(initial_center_in_cartesian_after_1st_rotation[0],
    #                                    initial_center_in_cartesian_after_1st_rotation[1],
    #                                    initial_center_in_cartesian_after_1st_rotation[2])))}")
    # print(f"Target center vector: {np.rad2deg(np.array(mapper.calculator
    #       .convertCartesianToSpherical(target_center_in_cartesian_after_1st_rotation[0],
    #                                    target_center_in_cartesian_after_1st_rotation[1],
    #                                    target_center_in_cartesian_after_1st_rotation[2])))}")
    # print(f"Meridian vector: {np.rad2deg(np.array(mapper.calculator
    #       .convertCartesianToSpherical(meridian_vector_in_cartesian_after_1st_rotation[0],
    #                                    meridian_vector_in_cartesian_after_1st_rotation[1],
    #                                    meridian_vector_in_cartesian_after_1st_rotation[2])))}")
    # print("-------------------------------------------------------")
    # print("Vectors after first rotation in cartesian coordinates: ")
    # print(f"Central vector: {initial_center_in_cartesian_after_1st_rotation}")
    # print(f"Target center vector: {target_center_in_cartesian_after_1st_rotation}")
    # print(f"Meridian vector: {meridian_vector_in_cartesian_after_1st_rotation}")
    # initial_center_in_cartesian_after_2nd_rotation = meridian_rotation @ initial_center_in_cartesian_after_1st_rotation
    # target_center_in_cartesian_after_2nd_rotation = meridian_rotation @ target_center_in_cartesian_after_1st_rotation
    # meridian_vector_in_cartesian_after_2nd_rotation = meridian_rotation @ meridian_vector_in_cartesian_after_1st_rotation
    # print("-------------------------------------------------------")
    # print("Vectors after second rotation in spherical coordinates: ")
    # print(f"Initial central vector: {np.rad2deg(np.array(mapper.calculator
    #                                                      .convertCartesianToSpherical(initial_center_in_cartesian_after_2nd_rotation[0],
    #                                                                                   initial_center_in_cartesian_after_2nd_rotation[1],
    #                                                                                   initial_center_in_cartesian_after_2nd_rotation[2]))) }")
    # print(f"Target center vector: {np.rad2deg(np.array(mapper.calculator
    #                                     .convertCartesianToSpherical(target_center_in_cartesian_after_2nd_rotation[0],
    #                                                                  target_center_in_cartesian_after_2nd_rotation[1],
    #                                                                  target_center_in_cartesian_after_2nd_rotation[2])))}")
    # print(f"Meridian vector: {np.rad2deg(np.array(mapper.calculator
    #                                .convertCartesianToSpherical(meridian_vector_in_cartesian_after_2nd_rotation[0],
    #                                                             meridian_vector_in_cartesian_after_2nd_rotation[1],
    #                                                             meridian_vector_in_cartesian_after_2nd_rotation[2])))}")
    # print("-------------------------------------------------------")
    # print("Vectors after second rotation in cartesian coordinates: ")
    # print(f"Central vector: {initial_center_in_cartesian_after_2nd_rotation}")
    # print(f"Target center vector: {target_center_in_cartesian_after_2nd_rotation}")
    # print(f"Meridian vector: {meridian_vector_in_cartesian_after_2nd_rotation}")
    # combined_rotation = meridian_rotation @ central_rotation
    # print("-------------------------------------------------------")
    # print(f"Combined rotation: \n{combined_rotation}")
    # initial_center_in_cartesian_after_combined_rotation = combined_rotation @ initial_center_in_cartesian
    # target_center_in_cartesian_after_combined_rotation = combined_rotation @ target_center_in_cartesian
    # meridian_vector_in_cartesian_after_combined_rotation = combined_rotation @ meridian_vector_in_cartesian
    # print("-------------------------------------------------------")
    # print("Vectors after combined rotation in spherical coordinates: ")
    # print(f"Initial central vector: {np.rad2deg(np.array(mapper.calculator
    #                                                      .convertCartesianToSpherical(initial_center_in_cartesian_after_combined_rotation[0],
    #                                                                                   initial_center_in_cartesian_after_combined_rotation[1],
    #                                                                                   initial_center_in_cartesian_after_combined_rotation[2]))) }")
    # print(f"Target center vector: {np.rad2deg(np.array(mapper.calculator
    #                                                    .convertCartesianToSpherical(target_center_in_cartesian_after_combined_rotation[0],
    #                                                                                 target_center_in_cartesian_after_combined_rotation[1],
    #                                                                                 target_center_in_cartesian_after_combined_rotation[2])))}")
    # print(f"Meridian vector: {np.rad2deg(np.array(mapper.calculator
    #                                               .convertCartesianToSpherical(meridian_vector_in_cartesian_after_combined_rotation[0],
    #                                                                            meridian_vector_in_cartesian_after_combined_rotation[1],
    #                                                                            meridian_vector_in_cartesian_after_combined_rotation[2])))}")
    # print("-------------------------------------------------------")
    # print("Vectors after combined rotation in cartesian coordinates: ")
    # print(f"Central vector: {initial_center_in_cartesian_after_combined_rotation}")
    # print(f"Target center vector: {target_center_in_cartesian_after_combined_rotation}")
    # print(f"Meridian vector: {meridian_vector_in_cartesian_after_combined_rotation}")

#---------------
def cli() -> None:
    parser = argparse.ArgumentParser(
        prog="ib-map",
        description="Generates a map based on the IBEX data file",
    )
    parser.add_argument(
        "link",
        help="Path to the file (e.g., t2010_02.txt))",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Disable banner and execution time information",
    )
    parser.add_argument(
        "-s", "--spinner",
        action="store_true",
        default=True,          # show spinner unless --quiet
        help="Show animated progress indicator (enabled by default)",
    )
    args = parser.parse_args()

    # Suppress spinner if user explicitly asked for --quiet
    show_spinner = args.spinner and not args.quiet

    if not args.quiet:
        print(INTRO_MESSAGE)

    t0 = time.time()
    run(args.link, show_spinner)
    if not args.quiet:
        print(f"--- {time.time() - t0:.2f} s ---")


#--------------
if __name__ == "__main__":
    # start_time = time.time()
    # main()
    # print("--- %s seconds ---" % (round(time.time() - start_time, 2)))
    cli()
    