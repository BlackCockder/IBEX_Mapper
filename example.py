import IBEXMapper as ibex

# Default.
ibex.addCircle("Testing circle 1", (10, 30))
ibex.generateSingleMapFromGivenFilePath(r'D:\CodingProjects\UKSWProjects\IBEX_Mapper\t2010_02.txt')

# We change DPI and disallow negative values.
ibex.setDefaultConfig(ibex.createNewConfig({
    "map_accuracy": 440,
    "allow_negative_values": False
}))
ibex.generateSingleMapFromGivenFilePath(r'D:\CodingProjects\UKSWProjects\IBEX_Mapper\t2010_02.txt')

# Enable rotation and rotate only by central rotation.
ibex.setDefaultConfig(ibex.createNewConfig({
    "rotate": True,
    "central_point": (-70, 0),
    "meridian_point": (-70, 0),
}))
ibex.generateSingleMapFromGivenFilePath(r'D:\CodingProjects\UKSWProjects\IBEX_Mapper\t2010_02.txt')

# Enable second rotation by placing meridian point on the right top side of central point
ibex.setDefaultConfig(ibex.createNewConfig({
    "meridian_point": (-90, 10),
}))
ibex.generateSingleMapFromGivenFilePath(r'D:\CodingProjects\UKSWProjects\IBEX_Mapper\t2010_02.txt')

# We reset the config and get back to te baseline
ibex.resetConfigToDefaultConfig()

ibex.setDefaultConfig(ibex.createNewConfig({
    "map_accuracy": 440,
    "allow_negative_values": False
}))
# And add our first point, that will be a blue x without a name on (-70, 30)
ibex.addPoint("Testing point 1", (-70, 30), "b", False, "x")
ibex.generateSingleMapFromGivenFilePath(r'D:\CodingProjects\UKSWProjects\IBEX_Mapper\t2010_02.txt')

# Now rotate back to our new central and cartesian
ibex.setDefaultConfig(ibex.createNewConfig({
    "rotate": True,
    "central_point": (-70, 0),
    "meridian_point": (-90, 10),
}))
ibex.generateSingleMapFromGivenFilePath(r'D:\CodingProjects\UKSWProjects\IBEX_Mapper\t2010_02.txt')

# Now we will add some texts. They are static, so rotation is not an issue.
ibex.removePoint("Testing point 1")
ibex.addMapText("Lets see if I work", (16, 16), 'b', 20, 90)
ibex.generateSingleMapFromGivenFilePath(r'D:\CodingProjects\UKSWProjects\IBEX_Mapper\t2010_02.txt')

# Now we will remove the text and add a circle, that will be a great circle by default.
ibex.removeMapText("Lets see if I work")
ibex.addCircle("Testing circle 1", (10, 30))
ibex.generateSingleMapFromGivenFilePath(r'D:\CodingProjects\UKSWProjects\IBEX_Mapper\t2010_02.txt')

# Now we will manipulate the scale a little bit.
ibex.removeMapText("Lets see if I work")
ibex.changeHeatmapScale((10, 30))
ibex.generateSingleMapFromGivenFilePath(r'D:\CodingProjects\UKSWProjects\IBEX_Mapper\t2010_02.txt')

# And now we will change the color palette to something else.
ibex.resetHeatmapScaleToDefault()
ibex.selectHeatmapColorPalette("batlow")
ibex.changeHeatmapScale((10, 30))
ibex.generateSingleMapFromGivenFilePath(r'D:\CodingProjects\UKSWProjects\IBEX_Mapper\t2010_02.txt')


# Now we will save the PDF file with this image to some other output.
# I give here a path to my own folder that well, doesn't exist yet. App will create the folder for me
# (if it detects that path is valid) and dump the file there.
ibex.generateSingleMapFromGivenFilePath(r'D:\CodingProjects\UKSWProjects\IBEX_Mapper\t2010_02.txt', r"D:\GitS\testcase")
