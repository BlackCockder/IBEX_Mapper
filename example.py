import IBEXMapper as ibex

filepath = r'D:\CodingProjects\UKSWProjects\IBEX_Mapper\t2010_02.txt'
output_path = r"D:\GitS\testcase"

# We print selected file path into default mollweide projection map that is saved in .output/ folder.
ibex.generateSingleMapFromGivenFilePath(filepath)

# We use setDefaultConfig and createNewConfig to update our default config to have 440x440 raster size and
# filter out all of negative values.
ibex.setDefaultConfig(ibex.createNewConfig({
    "map_accuracy": 440,
    "allow_negative_values": False
}))

# And generate
ibex.generateSingleMapFromGivenFilePath(filepath)

# Enable rotation and rotate only by central rotation.
ibex.setDefaultConfig(ibex.createNewConfig({
    "rotate": True,
    "central_point": (-70, 0),
    "meridian_point": (-70, 0),
}))
ibex.generateSingleMapFromGivenFilePath(filepath)

# Enable second rotation by placing meridian point on the right top side of central point
ibex.setDefaultConfig(ibex.createNewConfig({
    "meridian_point": (-90, 10),
}))
ibex.generateSingleMapFromGivenFilePath(filepath)

# We reset the config and get back to te baseline
ibex.resetConfigToDefaultConfig()

ibex.setDefaultConfig(ibex.createNewConfig({
    "map_accuracy": 440,
    "allow_negative_values": False
}))
# And add our first point, that will be a blue x without a name on (-70, 30)
ibex.addPoint("Testing point 1", (-70, 30), "b", False, "o", True)
ibex.generateSingleMapFromGivenFilePath(filepath)

# Now rotate back to our new central and cartesian
ibex.setDefaultConfig(ibex.createNewConfig({
    "rotate": True,
    "central_point": (-70, 0),
    "meridian_point": (-90, 10),
}))
ibex.generateSingleMapFromGivenFilePath(filepath)

# Now we will add some texts. They are static, so rotation is not an issue.
ibex.removePoint("Testing point 1")
ibex.addMapText("Lets see if I work", (16, 16), 'b', 20, 90)
ibex.generateSingleMapFromGivenFilePath(filepath)

# Now we will remove the text and add a circle, that will be a great circle by default.
ibex.removeMapText("Lets see if I work")
ibex.addCircle("Testing circle 1", (10, 30))
ibex.generateSingleMapFromGivenFilePath(filepath)

# Now we will manipulate the scale a little bit.
ibex.removeMapText("Lets see if I work")
ibex.changeHeatmapScale((10, 30))
ibex.generateSingleMapFromGivenFilePath(filepath)

# And now we will change the color palette to something else.
ibex.resetHeatmapScaleToDefault()
ibex.selectHeatmapColorPalette("batlow")
ibex.changeHeatmapScale((10, 30))
ibex.generateSingleMapFromGivenFilePath(filepath)


# Now we will save the PDF file with this image to some other output.
# I give here a path to my own folder that well, doesn't exist yet. App will create the folder for me
# (if it detects that path is valid) and dump the file there.
ibex.generateSingleMapFromGivenFilePath(filepath, output_path)

# All getters to check the current config and map features.
print(ibex.getDefaultConfig())
print(ibex.getMapFeatures())

# Now we want to not use default config, so we declare new one.
custom_config = ibex.createNewConfig({
        "map_accuracy": 720,
        "rotate": True,
        "central_point": (100, 0),
        "meridian_point": (35, -42),
        "allow_negative_values": False,
        "map_features_type_checking": True
})

# And can generate file directly using this config, without overwriting default config.
# Note: Map features are global still.
ibex.generateSingleMapFromGivenFilePath(filepath, output_path, custom_config)

# Now lets clean map
ibex.cleanMap()
ibex.generateSingleMapFromGivenFilePath(filepath, output_path)

# Type checking. We cannot input wrong data to most inputs, most certainly config file and
# all map features. Here are commented examples:
# ibex.addPoint((43, "4"), "gf", )
# ibex.setDefaultConfig(ibex.createNewConfig({
#     "not_part of the config": 33,
#     "map_accuracy": "no"
# }))
# ibex.generateSingleMapFromGivenFilePath(filepath, output_path)

# Finally, we still can disable type checking (if user wants to use more matplotlib colors
# or settings), but it is not suggested.
ibex.toggleTypeChecking()
# ibex.addPoint((43, "4"), "gf", ) # This will work now but generate error when map projecting.
