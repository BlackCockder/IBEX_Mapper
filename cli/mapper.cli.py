import time
import numpy as np
import IBEXMapper as ib


def main() -> None:
    mapper = ib.getObjectInstance()
    mapper.setDefaultConfig(mapper.generateConfigFromPartialInfo({
        "map_accuracy": 720,
        "rotate": True,
        "location_of_central_point": np.array([100, 5]),
        "meridian_point": np.array([80, 20])
    }))
    mapper.generateMapFromLink("t2010_02.txt")
    np.set_printoptions(precision=8, suppress=True, floatmode='fixed')
    config = mapper.formatConfigDatastructures(mapper.getDefaultConfig())
    initial_center = np.array([0, 0])
    target_center = config["location_of_central_point"]
    meridian_vector = config["meridian_point"]
    print("-------------------------------------------------------")
    print("Vectors in degrees:")
    print(f"Central vector: {initial_center}")
    print(f"Target center vector: {target_center}")
    print(f"Meridian vector: {meridian_vector}")
    initial_center_in_cartesian = mapper.configurator.convertSphericalToCartesianForPoints(initial_center)
    target_center_in_cartesian = mapper.configurator.convertSphericalToCartesianForPoints(target_center)
    meridian_vector_in_cartesian = mapper.configurator.convertSphericalToCartesianForPoints(meridian_vector)
    print("-------------------------------------------------------")
    print("Vectors in cartesian coordinates: ")
    print(f"Central vector: {initial_center_in_cartesian}")
    print(f"Target center vector: {target_center_in_cartesian}")
    print(f"Meridian vector: {meridian_vector_in_cartesian}")
    central_rotation = mapper.configurator.buildCenteringRotation(target_center)
    meridian_rotation = mapper.configurator.buildMeridianRotation(meridian_vector, central_rotation)
    print("-------------------------------------------------------")
    print("Rotations: ")
    print(f"Central rotation: \n{central_rotation}")
    print(f"Meridian rotation: \n{meridian_rotation}")
    initial_center_in_cartesian_after_1st_rotation = central_rotation @ initial_center_in_cartesian
    target_center_in_cartesian_after_1st_rotation = central_rotation @ target_center_in_cartesian
    meridian_vector_in_cartesian_after_1st_rotation = central_rotation @ meridian_vector_in_cartesian
    print("-------------------------------------------------------")
    print("Vectors after first rotation in spherical coordinates: ")
    print(f"Initial central vector: {np.rad2deg(np.array(mapper.calculator
          .convertCartesianToSpherical(initial_center_in_cartesian_after_1st_rotation[0],
                                       initial_center_in_cartesian_after_1st_rotation[1],
                                       initial_center_in_cartesian_after_1st_rotation[2])))}")
    print(f"Target center vector: {np.rad2deg(np.array(mapper.calculator
          .convertCartesianToSpherical(target_center_in_cartesian_after_1st_rotation[0],
                                       target_center_in_cartesian_after_1st_rotation[1],
                                       target_center_in_cartesian_after_1st_rotation[2])))}")
    print(f"Meridian vector: {np.rad2deg(np.array(mapper.calculator
          .convertCartesianToSpherical(meridian_vector_in_cartesian_after_1st_rotation[0],
                                       meridian_vector_in_cartesian_after_1st_rotation[1],
                                       meridian_vector_in_cartesian_after_1st_rotation[2])))}")
    print("-------------------------------------------------------")
    print("Vectors after first rotation in cartesian coordinates: ")
    print(f"Central vector: {initial_center_in_cartesian_after_1st_rotation}")
    print(f"Target center vector: {target_center_in_cartesian_after_1st_rotation}")
    print(f"Meridian vector: {meridian_vector_in_cartesian_after_1st_rotation}")
    initial_center_in_cartesian_after_2nd_rotation = meridian_rotation @ initial_center_in_cartesian_after_1st_rotation
    target_center_in_cartesian_after_2nd_rotation = meridian_rotation @ target_center_in_cartesian_after_1st_rotation
    meridian_vector_in_cartesian_after_2nd_rotation = meridian_rotation @ meridian_vector_in_cartesian_after_1st_rotation
    print("-------------------------------------------------------")
    print("Vectors after second rotation in spherical coordinates: ")
    print(f"Initial central vector: {np.rad2deg(np.array(mapper.calculator
                                                         .convertCartesianToSpherical(initial_center_in_cartesian_after_2nd_rotation[0],
                                                                                      initial_center_in_cartesian_after_2nd_rotation[1],
                                                                                      initial_center_in_cartesian_after_2nd_rotation[2]))) }")
    print(f"Target center vector: {np.rad2deg(np.array(mapper.calculator
                                        .convertCartesianToSpherical(target_center_in_cartesian_after_2nd_rotation[0],
                                                                     target_center_in_cartesian_after_2nd_rotation[1],
                                                                     target_center_in_cartesian_after_2nd_rotation[2])))}")
    print(f"Meridian vector: {np.rad2deg(np.array(mapper.calculator
                                   .convertCartesianToSpherical(meridian_vector_in_cartesian_after_2nd_rotation[0],
                                                                meridian_vector_in_cartesian_after_2nd_rotation[1],
                                                                meridian_vector_in_cartesian_after_2nd_rotation[2])))}")
    print("-------------------------------------------------------")
    print("Vectors after second rotation in cartesian coordinates: ")
    print(f"Central vector: {initial_center_in_cartesian_after_2nd_rotation}")
    print(f"Target center vector: {target_center_in_cartesian_after_2nd_rotation}")
    print(f"Meridian vector: {meridian_vector_in_cartesian_after_2nd_rotation}")
    combined_rotation = meridian_rotation @ central_rotation
    print("-------------------------------------------------------")
    print(f"Combined rotation: \n{combined_rotation}")
    initial_center_in_cartesian_after_combined_rotation = combined_rotation @ initial_center_in_cartesian
    target_center_in_cartesian_after_combined_rotation = combined_rotation @ target_center_in_cartesian
    meridian_vector_in_cartesian_after_combined_rotation = combined_rotation @ meridian_vector_in_cartesian
    print("-------------------------------------------------------")
    print("Vectors after combined rotation in spherical coordinates: ")
    print(f"Initial central vector: {np.rad2deg(np.array(mapper.calculator
                                                         .convertCartesianToSpherical(initial_center_in_cartesian_after_combined_rotation[0],
                                                                                      initial_center_in_cartesian_after_combined_rotation[1],
                                                                                      initial_center_in_cartesian_after_combined_rotation[2]))) }")
    print(f"Target center vector: {np.rad2deg(np.array(mapper.calculator
                                                       .convertCartesianToSpherical(target_center_in_cartesian_after_combined_rotation[0],
                                                                                    target_center_in_cartesian_after_combined_rotation[1],
                                                                                    target_center_in_cartesian_after_combined_rotation[2])))}")
    print(f"Meridian vector: {np.rad2deg(np.array(mapper.calculator
                                                  .convertCartesianToSpherical(meridian_vector_in_cartesian_after_combined_rotation[0],
                                                                               meridian_vector_in_cartesian_after_combined_rotation[1],
                                                                               meridian_vector_in_cartesian_after_combined_rotation[2])))}")
    print("-------------------------------------------------------")
    print("Vectors after combined rotation in cartesian coordinates: ")
    print(f"Central vector: {initial_center_in_cartesian_after_combined_rotation}")
    print(f"Target center vector: {target_center_in_cartesian_after_combined_rotation}")
    print(f"Meridian vector: {meridian_vector_in_cartesian_after_combined_rotation}")


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (round(time.time() - start_time, 2)))
