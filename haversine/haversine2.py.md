```python
from enum import Enum
from math import pi
from typing import Union, Tuple
import math


# mean earth radius - https://en.wikipedia.org/wiki/Earth_radius#Mean_radius
_AVG_EARTH_RADIUS_KM = 6371.0088
```

# Unit

Enumeration of supported distance units for haversine calculations.

| Value | Abbreviation |
|-------|-------------|
| `KILOMETERS` | `'km'` |
| `METERS` | `'m'` |
| `MILES` | `'mi'` |
| `NAUTICAL_MILES` | `'nmi'` |
| `FEET` | `'ft'` |
| `INCHES` | `'in'` |
| `RADIANS` | `'rad'` |
| `DEGREES` | `'deg'` |

Can be iterated: `tuple(Unit)` returns all supported units.

```python
class Unit(str, Enum):
    KILOMETERS = 'km'
    METERS = 'm'
    MILES = 'mi'
    NAUTICAL_MILES = 'nmi'
    FEET = 'ft'
    INCHES = 'in'
    RADIANS = 'rad'
    DEGREES = 'deg'
```

```python
class Unit(str, Enum):
    KILOMETERS = 'km'
    METERS = 'm'
    MILES = 'mi'
    NAUTICAL_MILES = 'nmi'
    FEET = 'ft'
    INCHES = 'in'
    RADIANS = 'rad'
    DEGREES = 'deg'
```

# Direction

Enumeration of cardinal and intercardinal compass directions.

Angles are expressed in **radians**, measured clockwise from North.

| Direction | Radians |
|-----------|---------|
| `NORTH` | `0.0` |
| `NORTHEAST` | `π × 0.25` |
| `EAST` | `π × 0.5` |
| `SOUTHEAST` | `π × 0.75` |
| `SOUTH` | `π` |
| `SOUTHWEST` | `π × 1.25` |
| `WEST` | `π × 1.5` |
| `NORTHWEST` | `π × 1.75` |

Can be iterated: `tuple(Direction)` returns all supported directions.

```python
class Direction(float, Enum):
    NORTH = 0.0
    NORTHEAST = pi * 0.25
    EAST = pi * 0.5
    SOUTHEAST = pi * 0.75
    SOUTH = pi
    SOUTHWEST = pi * 1.25
    WEST = pi * 1.5
    NORTHWEST = pi * 1.75


# Unit values taken from http://www.unitconversion.org/unit_converter/length.html
_CONVERSIONS = {
    Unit.KILOMETERS:       1.0,
    Unit.METERS:           1000.0,
    Unit.MILES:            0.621371192,
    Unit.NAUTICAL_MILES:   0.539956803,
    Unit.FEET:             3280.839895013,
    Unit.INCHES:           39370.078740158,
    Unit.RADIANS:          1/_AVG_EARTH_RADIUS_KM,
    Unit.DEGREES:          (1/_AVG_EARTH_RADIUS_KM)*(180.0/pi)
}


def get_avg_earth_radius(unit):
    return _AVG_EARTH_RADIUS_KM * _CONVERSIONS[unit]
```

# _normalize

Wraps a latitude/longitude pair into valid ranges:
- **Latitude**: `[-90, 90]`
- **Longitude**: `[-180, 180]`

Handles pole-crossing by reflecting latitude and shifting longitude by 180°.

- **Input**: `lat` (float), `lon` (float) — raw coordinate values (may be out of range)
- **Output**: `(lat, lon)` tuple — normalized coordinates

```python
def _normalize(lat: float, lon: float) -> Tuple[float, float]:
    lat = (lat + 90) % 360 - 90
    if lat > 90:
        lat = 180 - lat
        lon += 180
    lon = (lon + 180) % 360 - 180
    return lat, lon
```

# _normalize_vector

Vectorized version of `_normalize` for NumPy arrays.

Wraps latitude/longitude arrays into valid ranges:
- **Latitude**: `[-90, 90]`
- **Longitude**: `[-180, 180]`

Pole-crossing rows (where `lat > 90` after mod) are reflected and their
longitudes are shifted by 180°.

- **Input**: `lat` (ndarray), `lon` (ndarray)
- **Output**: `(lat, lon)` tuple of normalized ndarrays

```python
def _normalize_vector(lat: "numpy.ndarray", lon: "numpy.ndarray") -> Tuple["numpy.ndarray", "numpy.ndarray"]:
    lat = (lat + 90) % 360 - 90
    lon = (lon + 180) % 360 - 180
    wrap = lat > 90
    if numpy.any(wrap):
        lat[wrap] = 180 - lat[wrap]
        lon[wrap] = lon[wrap] % 360 - 180
    return lat, lon
```

# _ensure_lat_lon

Validates that a latitude/longitude pair is within proper geographic bounds.

Raises a `ValueError` if:
- `lat` is outside `[-90, 90]`
- `lon` is outside `[-180, 180]`

- **Input**: `lat` (float), `lon` (float)
- **Output**: `None` (raises on invalid input)

```python
def _ensure_lat_lon(lat: float, lon: float):
    if lat < -90 or lat > 90:
        raise ValueError(f"Latitude {lat} is out of range [-90, 90]")
    if lon < -180 or lon > 180:
        raise ValueError(f"Longitude {lon} is out of range [-180, 180]")
```

# _ensure_lat_lon_vector

Vectorized version of `_ensure_lat_lon` for NumPy arrays.

Raises a `ValueError` if any value in `lat` is outside `[-90, 90]`
or any value in `lon` is outside `[-180, 180]`.

- **Input**: `lat` (ndarray), `lon` (ndarray)
- **Output**: `None` (raises on invalid input)

```python
def _ensure_lat_lon_vector(lat: "numpy.ndarray", lon: "numpy.ndarray"):
    if numpy.abs(lat).max() > 90:
        raise ValueError("Latitude(s) out of range [-90, 90]")
    if numpy.abs(lon).max() > 180:
        raise ValueError("Longitude(s) out of range [-180, 180]")


def _explode_args(f):
    return lambda ops: f(**ops.__dict__)
```

# _create_haversine_kernel

Factory that builds a haversine distance kernel using the provided math operations object.

The kernel computes the **great-circle angular distance** (in radians) on a unit sphere
between two points given in degrees. Accepts either scalar (`math`) or array (`numpy`) ops.

Uses the haversine formula:
```
d = 2 * arcsin(sqrt(sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)))
```

> **Note**: `2 * atan2(sqrt(d), sqrt(1-d))` is more accurate near antipodal points
> but slower. The simpler `arcsin` form is used here.

- **Input**: `ops` — object with math functions (`sin`, `cos`, `asin`/`arcsin`, `sqrt`, `radians`)
- **Output**: `_haversine_kernel(lat1, lng1, lat2, lng2)` — angular distance in radians

```python
@_explode_args
def _create_haversine_kernel(*, asin=None, arcsin=None, cos, radians, sin, sqrt, **_):
    asin = asin or arcsin

    def _haversine_kernel(lat1, lng1, lat2, lng2):
        lat1 = radians(lat1)
        lng1 = radians(lng1)
        lat2 = radians(lat2)
        lng2 = radians(lng2)
        lat = lat2 - lat1
        lng = lng2 - lng1
        d = (sin(lat * 0.5) ** 2
             + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2)
        # Note: 2 * atan2(sqrt(d), sqrt(1-d)) is more accurate at
        # large distance (d is close to 1), but also slower.
        return 2 * asin(sqrt(d))
    return _haversine_kernel
```

# _create_inverse_haversine_kernel

Factory that builds an inverse haversine kernel using the provided math operations object.

Given an origin point, a bearing (direction), and a distance on a unit sphere,
computes the **destination point** using the inverse haversine formula:

```
φ2 = arcsin(cos(d)·sin(φ1) + sin(d)·cos(φ1)·cos(θ))
λ2 = λ1 + atan2(sin(θ)·sin(d)·cos(φ1), cos(d) − sin(φ1)·sin(φ2))
```

where `φ` = latitude, `λ` = longitude, `d` = angular distance, `θ` = bearing.

- **Input**: `ops` — object with math functions (`sin`, `cos`, `asin`/`arcsin`, `atan2`/`arctan2`, `degrees`, `radians`)
- **Output**: `_inverse_haversine_kernel(lat, lng, direction, d)` — `(lat, lon)` of destination in degrees

```python
@_explode_args
def _create_inverse_haversine_kernel(*, asin=None, arcsin=None, atan2=None, arctan2=None, cos, degrees, radians, sin, sqrt, **_):
    asin = asin or arcsin
    atan2 = atan2 or arctan2

    def _inverse_haversine_kernel(lat, lng, direction, d):
        lat = radians(lat)
        lng = radians(lng)
        cos_d, sin_d = cos(d), sin(d)
        cos_lat, sin_lat = cos(lat), sin(lat)
        sin_d_cos_lat = sin_d * cos_lat
        return_lat = asin(cos_d * sin_lat + sin_d_cos_lat * cos(direction))
        return_lng = lng + atan2(sin(direction) * sin_d_cos_lat,
                                 cos_d - sin_lat * sin(return_lat))
        return degrees(return_lat), degrees(return_lng)
    return _inverse_haversine_kernel


_haversine_kernel = _create_haversine_kernel(math)
_inverse_haversine_kernel = _create_inverse_haversine_kernel(math)

try:
    import numpy
    has_numpy = True
    _haversine_kernel_vector = _create_haversine_kernel(numpy)
    _inverse_haversine_kernel_vector = _create_inverse_haversine_kernel(numpy)
except ModuleNotFoundError:
    # Import error will be reported in haversine_vector() / inverse_haversine_vector()
    has_numpy = False

try:
    import numba # type: ignore
    if has_numpy:
        _haversine_kernel_vector = numba.vectorize(fastmath=True)(_haversine_kernel_vector)
        # Tuple output is not supported for numba.vectorize. Just jit the numpy version.
        _inverse_haversine_kernel_vector = numba.njit(fastmath=True)(_inverse_haversine_kernel_vector)
    _haversine_kernel = numba.njit(_haversine_kernel)
    _inverse_haversine_kernel = numba.njit(_inverse_haversine_kernel)
except ModuleNotFoundError:
    pass
```

# haversine

Calculates the great-circle distance between two points on Earth's surface.

Uses the [Haversine formula](https://en.wikipedia.org/wiki/Haversine_formula),
which gives the shortest distance over the Earth's surface (ignoring elevation).

- **Input**:
  - `point1` — `(latitude, longitude)` in decimal degrees
  - `point2` — `(latitude, longitude)` in decimal degrees
  - `unit` — a `Unit` member or its string abbreviation (default: `'km'`)
  - `normalize` — if `True`, wrap coordinates into valid ranges before computing
  - `check` — if `True`, raise `ValueError` for out-of-range coordinates

- **Output**: distance as a `float` in the requested unit

**Examples:**
```python
haversine((45.7597, 4.8422), (48.8567, 2.3508))
# 392.2172595594006  (km)

haversine((45.7597, 4.8422), (48.8567, 2.3508), unit=Unit.MILES)
# 243.71250609539816

haversine((45.7597, 4.8422), (48.8567, 2.3508), unit='m')
# 392217.2595594006
```

```python
def haversine(point1, point2, unit=Unit.KILOMETERS, normalize=False, check=True):

    # unpack latitude/longitude
    lat1, lng1 = point1
    lat2, lng2 = point2

    # normalize points or ensure they are proper lat/lon, i.e., in [-90, 90] and [-180, 180]
    if normalize:
        lat1, lng1 = _normalize(lat1, lng1)
        lat2, lng2 = _normalize(lat2, lng2)
    elif check:
        _ensure_lat_lon(lat1, lng1)
        _ensure_lat_lon(lat2, lng2)

    return get_avg_earth_radius(unit) * _haversine_kernel(lat1, lng1, lat2, lng2)
```

# haversine_vector

Vectorized haversine distance calculation using NumPy.

Functionally identical to `haversine`, but operates on **arrays of points**,
making it far more efficient for bulk distance calculations via NumPy vectorization.

- **Input**:
  - `array1` — array of `(lat, lon)` pairs, shape `(N, 2)`
  - `array2` — array of `(lat, lon)` pairs, shape `(N, 2)` (or any shape when `comb=True`)
  - `unit` — a `Unit` member or abbreviation (default: `'km'`)
  - `comb` — if `True`, compute all pairwise distances (combinatorial mode); arrays may differ in size
  - `normalize` — if `True`, wrap coordinates into valid ranges
  - `check` — if `True`, raise on out-of-range coordinates

- **Output**: ndarray of distances in the requested unit

**Examples:**
```python
# Element-wise distances (default)
haversine_vector([(0, 0), (10, 10)], [(1, 1), (11, 11)])
# array([157.2..., 157.2...])

# All pairwise distances (comb=True)
haversine_vector([(0, 0)], [(1, 1), (2, 2)], comb=True)
# array([[157.2..., 314.4...]])
```

> Requires NumPy. Raises `RuntimeError` if NumPy is unavailable.
> Optionally accelerated by Numba if installed.

```python
def haversine_vector(array1, array2, unit=Unit.KILOMETERS, comb=False, normalize=False, check=True):
    if not has_numpy:
        raise RuntimeError('Error, unable to import Numpy, '
                           'consider using haversine instead of haversine_vector.')

    # ensure arrays are numpy ndarrays
    if not isinstance(array1, numpy.ndarray):
        array1 = numpy.array(array1)
    if not isinstance(array2, numpy.ndarray):
        array2 = numpy.array(array2)

    # ensure will be able to iterate over rows by adding dimension if needed
    if array1.ndim == 1:
        array1 = numpy.expand_dims(array1, 0)
    if array2.ndim == 1:
        array2 = numpy.expand_dims(array2, 0)

    # Asserts that both arrays have same dimensions if not in combination mode
    if not comb:
        if array1.shape != array2.shape:
            raise IndexError(
                "When not in combination mode, arrays must be of same size. If mode is required, use comb=True as argument.")

    # unpack latitude/longitude
    lat1, lng1 = array1[:, 0], array1[:, 1]
    lat2, lng2 = array2[:, 0], array2[:, 1]

    # normalize points or ensure they are proper lat/lon, i.e., in [-90, 90] and [-180, 180]
    if normalize:
        lat1, lng1 = _normalize_vector(lat1, lng1)
        lat2, lng2 = _normalize_vector(lat2, lng2)
    elif check:
        _ensure_lat_lon_vector(lat1, lng1)
        _ensure_lat_lon_vector(lat2, lng2)

    # If in combination mode, turn coordinates of array1 into column vectors for broadcasting
    if comb:
        lat1 = numpy.expand_dims(lat1, axis=0)
        lng1 = numpy.expand_dims(lng1, axis=0)
        lat2 = numpy.expand_dims(lat2, axis=1)
        lng2 = numpy.expand_dims(lng2, axis=1)

    return get_avg_earth_radius(unit) * _haversine_kernel_vector(lat1, lng1, lat2, lng2)
```

# inverse_haversine

Computes the destination point reached by traveling a given distance from a starting point
in a specified direction along the Earth's surface.

This is the **inverse** of the haversine problem: instead of computing distance between
two known points, it finds the second point given origin, bearing, and distance.

- **Input**:
  - `point` — `(latitude, longitude)` of origin in decimal degrees
  - `distance` — distance to travel, in `unit`
  - `direction` — bearing as a `Direction` enum or float in **radians**
  - `unit` — unit of `distance` (default: `'km'`)
  - `normalize_output` — if `True`, wrap output coordinates into `[-90, 90]` / `[-180, 180]`

- **Output**: `(lat, lon)` of destination point in decimal degrees

**Examples:**
```python
inverse_haversine((48.8567, 2.3508), 1, Direction.NORTH)
# (48.865697..., 2.3508)  — 1 km north of Paris

inverse_haversine((0, 0), 111.195, Direction.EAST)
# (0.0, 1.0)  — ~1 degree east along the equator
```

```python
def inverse_haversine(point, distance, direction: Union[Direction, float], unit=Unit.KILOMETERS, normalize_output=False):
    lat, lng = point
    r = get_avg_earth_radius(unit)
    outLat, outLng = _inverse_haversine_kernel(lat, lng, direction, distance / r)

    if normalize_output:
        return _normalize(outLat, outLng)
    else:
        return (outLat, outLng)
```

# inverse_haversine_vector

Vectorized version of `inverse_haversine` for computing multiple destination points at once.

Takes arrays of origin points, distances, and directions and computes all destination
coordinates in parallel using NumPy.

- **Input**:
  - `array` — array of `(lat, lon)` origin pairs, shape `(N, 2)`
  - `distance` — array of distances (length `N`), in `unit`
  - `direction` — array of bearings in **radians** (length `N`)
  - `unit` — unit of distances (default: `'km'`)
  - `normalize_output` — if `True`, wrap output into valid lat/lon ranges

- **Output**: `(lat_array, lon_array)` — two ndarrays of destination coordinates in degrees

**Example:**
```python
import numpy as np
points = np.array([(48.8567, 2.3508), (51.5074, -0.1278)])
dists  = np.array([10.0, 20.0])
dirs   = np.array([Direction.NORTH, Direction.EAST])

inverse_haversine_vector(points, dists, dirs)
# (array([48.946..., 51.507...]), array([2.3508, 0.157...]))
```

> Requires NumPy. Raises `RuntimeError` if NumPy is unavailable.
> Optionally accelerated by Numba if installed.

```python
def inverse_haversine_vector(array, distance, direction, unit=Unit.KILOMETERS, normalize_output=False): # -> Tuple["numpy.ndarray", "numpy.ndarray"]:
    if not has_numpy:
        raise RuntimeError('Error, unable to import Numpy, '
                           'consider using inverse_haversine instead of inverse_haversine_vector.')

    # ensure arrays are numpy ndarrays
    array, distance, direction = map(numpy.asarray, (array, distance, direction))

    # ensure will be able to iterate over rows by adding dimension if needed
    if array.ndim == 1:
        array = numpy.expand_dims(array, 0)

    # Asserts that arrays are correctly sized
    if array.ndim != 2 or array.shape[1] != 2 or array.shape[0] != len(distance) or array.shape[0] != len(direction):
        raise IndexError("Arrays must be of same size.")

    # unpack latitude/longitude
    lat, lng = array[:, 0], array[:, 1]

    r = get_avg_earth_radius(unit)
    outLatArray, outLngArray = _inverse_haversine_kernel_vector(lat, lng, direction, distance/r)

    if normalize_output:
        return _normalize_vector(outLatArray, outLngArray)

    return (outLatArray, outLngArray)
```