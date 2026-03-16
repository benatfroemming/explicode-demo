"""
# Pipeline

End-to-end analysis pipeline. Loads a city dataset, computes a
[pairwise distance matrix](../geo/haversine.py?id=pairwise-distances),
runs [clustering](../geo/clustering.py?id=cluster-points), and prints
[summary statistics](../stats/descriptive.py?id=summary).

---

## City Dataset

A small set of world cities with their coordinates used as the default
input for the pipeline.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from geo.haversine import pairwise_distances, Coord
from geo.clustering import cluster_points, cluster_summary
from stats.descriptive import summary, print_summary

CITIES: dict[str, Coord] = {
    "New York":    (40.7128,  -74.0060),
    "London":      (51.5074,   -0.1278),
    "Tokyo":       (35.6762,  139.6503),
    "Sydney":      (-33.8688, 151.2093),
    "São Paulo":   (-23.5505,  -46.6333),
    "Cairo":       (30.0444,   31.2357),
    "Mumbai":      (19.0760,   72.8777),
    "Mexico City": (19.4326,  -99.1332),
    "Lagos":       (6.5244,    3.3792),
    "Beijing":     (39.9042,  116.4074),
}


"""
## Run Pipeline

1. Build the $n \times n$ distance matrix.
2. Flatten the upper triangle (excluding diagonal) into a 1-D list.
3. Print [descriptive statistics](../stats/descriptive.py?id=summary) on all pairwise distances.
4. Cluster cities within 8 000 km of each other and print the groups.

**`run_pipeline(cities, cluster_radius_km)`**

- `cities` *(dict[str, Coord])* — mapping of city name to `(latitude, longitude)`, defaults to `CITIES`
- `cluster_radius_km` *(float)* — radius used to group nearby cities, defaults to `8_000`
"""


def run_pipeline(cities: dict[str, Coord] = CITIES, cluster_radius_km: float = 8_000) -> None:
    names = list(cities.keys())
    coords = list(cities.values())
    n = len(coords)

    matrix = pairwise_distances(coords)
    flat = [matrix[i][j] for i in range(n) for j in range(i + 1, n)]

    print(f"Cities: {', '.join(names)}")
    print_summary(summary(flat, "all pairwise distances (km)"))

    clusters = cluster_points(coords, cluster_radius_km)
    csummary = cluster_summary(coords, clusters)

    print(f"\nClusters (radius = {cluster_radius_km:,} km): {len(clusters)} group(s)")
    for i, s in enumerate(csummary):
        members = [names[j] for j in clusters[i]]
        lat, lon = s["centroid"]
        print(f"  [{i+1}] {', '.join(members)}")
        print(f"       centroid ({lat:.1f}°, {lon:.1f}°)  spread {s['max_radius_km']:.0f} km")

    max_d = max(flat)
    min_d = min(flat)
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j] == max_d:
                print(f"\nLongest route:  {names[i]} ↔ {names[j]}  ({max_d:,.0f} km)")
            if matrix[i][j] == min_d:
                print(f"Shortest route: {names[i]} ↔ {names[j]}  ({min_d:,.0f} km)")


""" ## Run """

if __name__ == "__main__":
    run_pipeline()