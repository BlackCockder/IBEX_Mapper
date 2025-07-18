
# IBEX Mapper

IBEX Mapper is a Python library for creating and manipulating spherical maps with various features. It provides functionality for generating heatmaps, adding points, circles, and text annotations to maps, and configuring map projections.

## Authors

**Wiktor Tworzewski**  
Physics Student\
GitHub: [@xVeroNy](https://github.com/xVeroNy)

**Maciej Kobiela**  
Physics Student\
GitHub: [@BlackCockder](https://github.com/BlackCockder)


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

#### `generateSingleMapFromGivenFilePath(link, output_path, config=None)`
Generates a map from a data file.

**Parameters:**
- `link` (str): Path to the data file.
- `output_path` (str, optional): Path to folder where the file will be placed. It will make directories if needed.
Default is `output/` in app's root directory.
- `config` (dict, optional): Configuration dictionary. If not provided, the default configuration is used.

**Returns:**
- None: The function displays the generated map.

### Configuration Functions

#### `setDefaultConfig(config)`
Sets a new default configuration. Automatically turns all python datastructures into strings.
Intended use is with `createNewConfig(config)`.

**Parameters:**
- `config` (dict): Configuration dictionary with valid keys and values.

**Valid keys and values:**
- `map_accuracy` (int): Resolution of the map. Range: positive integers. Default is 400.
- `max_l_to_cache` (int): Maximum spherical harmonic degree to cache. Range: positive integers. Default is 30
- `rotate` (bool): Whether to rotate the map. Default is False
- `central_point` (tuple[float, float]): Center of the map in (longitude, latitude). Range: longitude [-180, 180], latitude [-90, 90]. Default is (0, 0).
- `meridian_point` (tuple[float, float]): Meridian reference point in (longitude, latitude). Range: longitude [-180, 180], latitude [-90, 90].  Default is (0, 0).
>  **Note:** If the user wants to apply only the first rotation (based on the central point), they can simply set the `central_point` to coordinates other than `(0, 0)`. The application assumes that if the `meridian_point` is left at `(0, 0)`, the second rotation will be skipped.
- `allow_negative_values` (bool): Whether to allow negative values in the heatmap.
- `map_features_type_checking` (bool): Whether to type-check all map features related functions.

#### `getDefaultConfig()`
Retrieves the current default configuration.

**Returns:**
- dict: The current default configuration. Contains python datastructures.

#### `resetConfigToDefaultConfig()`
Resets to the original default configuration.

**Returns:**
- None

#### `createNewConfig(config)`
Creates a valid configuration from partial information.

**Parameters:**
- `config` (dict): Partial configuration dictionary with valid keys and values. It is always type-checked.

**Returns:**
- dict: Complete configuration dictionary with default values for missing keys (as intended).

### Point Related Functions

#### `addPoint(point_name, coordinates, color="g", show_text=True, point_type="o")`
Adds a point to the map. Is type-checked by default.

**Parameters:**
- `point_name` (str): Name of the point.
- `coordinates` (tuple[float, float]): Coordinates of the point in (longitude, latitude). Range: longitude [-180, 180], latitude [-90, 90].
- `color` (str, optional): Color of the point. Default: "g" (green).
- `show_text` (bool, optional): Whether to show the point name. Default: True.
- `point_type` (str, optional): Type of point marker. Default: "o" (circle).
- `hollow` (str, optional): Whether to render a hollow point or not. Default if False

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

### Circle Related Functions

#### `addCircle(circle_name, coordinates_of_circle_center, angle=90, color="g", linestyle="-")`
Adds a circle to the map. It is type-checked by default.

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

### Text Relate Functions

#### `addMapText(text_name, coords, color, font_size=8, tilt_angle=0)`
Adds fixed (!) text to the map. It is type-checked by default.

**Parameters:**
- `text_name` (str): Name of the text.
- `coords` (tuple[float, float]): Coordinates of the text in (longitude, latitude). Range: longitude [-180, 180], latitude [-90, 90].
- `color` (str): Color of the text.
- `font_size` (int, optional): Font size of the text. Range: [4, 72]. Default: 8.
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

### Heatmap Related Functions

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
Toggles type checking for map features related functions.

**Returns:**
- None

## All Type-Check Valid Values for All Methods

This section outlines the expected types, ranges, and accepted values for each configurable or user-defined parameter used in IBEX Mapper. Inputs outside these constraints will raise `TypeError` or `ValueError`.

### Configuration Dictionary (`config`)

| Key                        | Type                                | Accepted Values / Range                                                                 |
|---------------------------|-------------------------------------|------------------------------------------------------------------------------------------|
| `map_accuracy`            | `int`                               | Must be a positive integer (`> 0`)                                                      |
| `max_l_to_cache`          | `int`                               | Must be a positive integer (`> 0`)                                                      |
| `rotate`                  | `bool` or `'True'` / `'False'`      | Boolean or string `'True'` / `'False'` (case-insensitive)                              |
| `allow_negative_values`   | `bool` or `'True'` / `'False'`      | Boolean or string `'True'` / `'False'` (case-insensitive)                              |
| `map_features_type_checking` | `bool` or `'True'` / `'False'`   | Boolean or string `'True'` / `'False'` (case-insensitive)                              |
| `central_point`           | `tuple[float, float]`               | Longitude in `[-180, 180]`, Latitude in `[-90, 90]`                                     |
| `meridian_point`          | `tuple[float, float]`               | Longitude in `[-180, 180]`, Latitude in `[-90, 90]`                                     |

---

### Coordinates

Used for: `coordinates`, `coords`, `central_point`, `meridian_point`

- Must be a `tuple[float, float]`
- Longitude: `[-180, 180]`
- Latitude: `[-90, 90]`

---

### Colors (for points, circles, text)

Accepted strings:

```
'b', 'g', 'r', 'c', 'm', 'y', 'k', 'w'
```

---

### Point Marker Types

Accepted strings for `point_type`:

```
'.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8',
's', 'p', 'P', '*', 'h', 'H', '+', 'x', 'X', 'D', 'd', '|', '_'
```

---

### Circle Parameters

| Parameter     | Type               | Accepted Values                                      |
|---------------|--------------------|------------------------------------------------------|
| `angle`       | `float` or `int`   | Range: (0, 360) — exclusive bounds                   |
| `linestyle`   | `str`              | `'solid'`, `'dashed'`, `'dashdot'`, `'dotted'`, `'-'`, `'--'`, `'-.'`, `':'` |

---

### Text Parameters

| Parameter     | Type               | Accepted Values                                      |
|---------------|--------------------|------------------------------------------------------|
| `font_size`   | `int`              | Range: [4, 72]                                       |
| `tilt_angle`  | `float` or `int`   | Range: [0, 360] (degrees, counterclockwise)          |

---

### Heatmap Scale

- Must be a `tuple[float, float]`
- Format: `(x, y)` where `x < y`
- Use `(0, 0)` for **automatic scaling** (default)

---

### Heatmap Color Palettes

Accepted strings:

```
'batlow', 'batlowK', 'batlowW', 'viridis', 'magma', 'plasma', 'inferno', 'cividis'
```


## File Structure

The IBEX Mapper project consists of the following main components:

- `IBEXMapper/__init__.py`: Main API functions
- `IBEXMapper/app.py`: Core application logic
- `IBEXMapper/calculator.py`: Mathematical operations and calculations
- `IBEXMapper/configurator.py`: Configuration and rotation handling
- `IBEXMapper/handler.py`: Data processing and validation
- `IBEXMapper/map_features.py`: Management of map features (points, circles, text)
- `IBEXMapper/projection.py`: Map projection and visualization
- `public/`: folder that contains color palettes data that app loads (for custom color palettes)

## Usage Example

Example code usage as packages is in `example.py` file.

This is NOT part of `example.py`, but it is valid example as well:
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

