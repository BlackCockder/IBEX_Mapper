# IBEX Mapper

IBEX Mapper is a Python library for creating and manipulating spherical maps with various features. It provides functionality for generating heatmaps, adding points, circles, and text annotations to maps, and configuring map projections.

## Features

- Generate spherical maps from data files
- Add, remove, and manage points, circles, and text annotations
- Configure map projection parameters
- Customize heatmap scales and color palettes
- Rotate maps to center on specific coordinates

## Dependencies

The IBEX Mapper library depends on the following Python packages:

- NumPy ver. 2.3.1: For numerical operations and array handling
- Matplotlib ver. 3.10.3: For plotting and visualization
- SciPy ver. 1.16.0: For scientific computing, specifically for spherical harmonics and spatial transformations

parts of Python standard library:
- JSON: For configuration and feature storage 
- OS: For file and directory operations 
- Pathlib: For path handling 

## API Reference

### Core Functions

#### `getObjectInstance()`
Returns the IBEXMapper instance.

**Returns:**
- IBEXMapper object: The singleton instance of the IBEXMapper class.

#### `generateSingleMapFromGivenFilePath(link, config=None)`
Generates a map from a data file.

**Parameters:**
- `link` (str): Path to the data file.
- `config` (dict, optional): Configuration dictionary. If not provided, the default configuration is used.

**Returns:**
- None: The function displays the generated map.

### Configuration Functions

#### `setDefaultConfig(config)`
Sets a new default configuration.

**Parameters:**
- `config` (dict): Configuration dictionary with valid keys and values.

**Valid keys and values:**
- `map_accuracy` (int): Resolution of the map. Range: positive integers, typically around 400.
- `max_l_to_cache` (int): Maximum spherical harmonic degree to cache. Range: positive integers, typically around 30.
- `rotate` (bool): Whether to rotate the map.
- `central_point` (tuple[float, float]): Center of the map in (longitude, latitude). Range: longitude [-180, 180], latitude [-90, 90].
- `meridian_point` (tuple[float, float]): Meridian reference point in (longitude, latitude). Range: longitude [-180, 180], latitude [-90, 90].
- `allow_negative_values` (bool): Whether to allow negative values in the heatmap.

#### `getDefaultConfig()`
Retrieves the current default configuration.

**Returns:**
- dict: The current default configuration.

#### `resetConfigToDefaultConfig()`
Resets to the original default configuration.

**Returns:**
- None

#### `createNewConfig(config)`
Creates a valid configuration from partial information.

**Parameters:**
- `config` (dict): Partial configuration dictionary with valid keys and values.

**Returns:**
- dict: Complete configuration dictionary with default values for missing keys.

### Point Management Functions

#### `addPoint(point_name, coordinates, color="g", show_text=True, point_type="o")`
Adds a point to the map.

**Parameters:**
- `point_name` (str): Name of the point.
- `coordinates` (tuple[float, float]): Coordinates of the point in (longitude, latitude). Range: longitude [-180, 180], latitude [-90, 90].
- `color` (str, optional): Color of the point. Default: "g" (green).
- `show_text` (bool, optional): Whether to show the point name. Default: True.
- `point_type` (str, optional): Type of point marker. Default: "o" (circle).

**Returns:**
- None

#### `removePoint(point_name)`
Removes a point from the map.

**Parameters:**
- `point_name` (str): Name of the point to remove.

**Returns:**
- None

#### `removeAllPoints()`
Removes all points from the map.

**Returns:**
- None

### Circle Management Functions

#### `addCircle(circle_name, coordinates_of_circle_center, angle=90, color="g", linestyle="-")`
Adds a circle to the map.

**Parameters:**
- `circle_name` (str): Name of the circle.
- `coordinates_of_circle_center` (tuple[float, float]): Coordinates of the circle center in (longitude, latitude). Range: longitude [-180, 180], latitude [-90, 90].
- `angle` (float, optional): Angle of the circle in degrees. Range: (0, 360). Default: 90.
- `color` (str, optional): Color of the circle. Default: "g" (green).
- `linestyle` (str, optional): Line style of the circle. Default: "-" (solid).

**Returns:**
- None

#### `removeCircle(circle_name)`
Removes a circle from the map.

**Parameters:**
- `circle_name` (str): Name of the circle to remove.

**Returns:**
- None

#### `removeAllCircles()`
Removes all circles from the map.

**Returns:**
- None

### Text Management Functions

#### `addMapText(text_name, coords, color, font_size=8, tilt_angle=0)`
Adds text to the map.

**Parameters:**
- `text_name` (str): Name of the text.
- `coords` (tuple[float, float]): Coordinates of the text in (longitude, latitude). Range: longitude [-180, 180], latitude [-90, 90].
- `color` (str): Color of the text.
- `font_size` (int, optional): Font size of the text. Range: [8, 72]. Default: 8.
- `tilt_angle` (int, optional): Tilt angle of the text in degrees. Range: [0, 360]. Default: 0.

**Returns:**
- None

#### `removeMapText(text_name)`
Removes text from the map.

**Parameters:**
- `text_name` (str): Name of the text to remove.

**Returns:**
- None

#### `removeAllMapText()`
Removes all text from the map.

**Returns:**
- None

### Heatmap Management Functions

#### `changeHeatmapScale(color)`
Changes the heatmap scale.

**Parameters:**
- `color` (tuple[float, float]): Scale for the heatmap. The first value must be less than the second value. Use (0, 0) for automatic scaling.

**Returns:**
- None

#### `resetHeatmapScaleToDefault()`
Resets the heatmap scale to default (0, 0).

**Returns:**
- None

#### `selectHeatmapColorPalette(color)`
Selects a heatmap color palette.

**Parameters:**
- `color` (str): Color palette name. Valid values include "viridis", "magma", "batlow", "batlowK", and "batlowW".

**Returns:**
- None

#### `resetHeatmapColorPalette()`
Resets the heatmap color palette to default ("magma").

**Returns:**
- None

### Utility Functions

#### `cleanMap()`
Clears all points, circles, texts, and resets heatmap settings.

**Returns:**
- None

#### `toggleTypeChecking()`
Toggles type checking for function parameters.

**Returns:**
- None

## File Structure

The IBEX Mapper project consists of the following main components:

- `IBEXMapper/__init__.py`: Main API functions
- `IBEXMapper/app.py`: Core application logic
- `IBEXMapper/calculator.py`: Mathematical operations and calculations
- `IBEXMapper/configurator.py`: Configuration and rotation handling
- `IBEXMapper/handler.py`: Data processing and validation
- `IBEXMapper/map_features.py`: Management of map features (points, circles, text)
- `IBEXMapper/projection.py`: Map projection and visualization

## Usage Example

```python
import IBEXMapper as ibex

# Generate a map from a data file
ibex.generateSingleMapFromGivenFilePath("path/to/data.txt")

# Add a point to the map
ibex.addPoint("Point1", (0, 0), color="r")

# Add a circle to the map
ibex.addCircle("Circle1", (30, 30), angle=45, color="b")

# Add text to the map
ibex.addMapText("Text1", (60, 60), color="g", font_size=12)

# Change the heatmap color palette
ibex.selectHeatmapColorPalette("viridis")

# Generate a map with custom configuration
config = ibex.createNewConfig({
    "map_accuracy": 600,
    "rotate": True,
    "central_point": (30, 30)
})
ibex.generateSingleMapFromGivenFilePath("path/to/data.txt", config)
```