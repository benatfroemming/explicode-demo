"""
# Clustering

Simple geographic clustering using a greedy radius-based approach.
No dependencies beyond the standard library — uses the
[Haversine distance](haversine.py?id=single-distance) function from the
sibling module.

---

## Algorithm

Given a set of points and a radius $r$ (in km), the algorithm works as
follows:

1. Pick the first unassigned point as a new cluster centre.
2. Assign every unassigned point within $r$ km of that centre to the
   same cluster.
3. Repeat until all points are assigned.

This is $O(n^2)$ but straightforward and works well for small datasets.
"""

from geo.haversine import haversine, Coord


"""
## Cluster Points

Group point indices into clusters where every member is within
`radius_km` of the cluster's seed point.

**`cluster_points(points, radius_km)`**

- `points` *(list[Coord])* — list of `(latitude, longitude)` pairs in decimal degrees
- `radius_km` *(float)* — maximum distance from the seed point to include in the cluster

*Returns* `list[list[int]]` — list of clusters, each a list of indices into `points`
"""


def cluster_points(points: list[Coord], radius_km: float) -> list[list[int]]:
    assigned = [False] * len(points)
    clusters: list[list[int]] = []

    for i, p in enumerate(points):
        if assigned[i]:
            continue
        cluster = [i]
        assigned[i] = True
        for j in range(i + 1, len(points)):
            if not assigned[j] and haversine(p, points[j]) <= radius_km:
                cluster.append(j)
                assigned[j] = True
        clusters.append(cluster)

    return clusters


"""
## Cluster Summary

Compute the centroid and spread of each cluster.

The centroid is the arithmetic mean of latitudes and longitudes —
accurate enough for small clusters, though for large geographic spreads
a spherical mean would be more precise.

**`cluster_summary(points, clusters)`**

- `points` *(list[Coord])* — original list of `(latitude, longitude)` pairs
- `clusters` *(list[list[int]])* — output from `cluster_points`

*Returns* `list[dict]` — one dict per cluster with keys `size`, `centroid`, and `max_radius_km`
"""


def cluster_summary(points: list[Coord], clusters: list[list[int]]) -> list[dict]:
    summaries = []
    for cluster in clusters:
        lats = [points[i][0] for i in cluster]
        lons = [points[i][1] for i in cluster]
        centroid = (sum(lats) / len(lats), sum(lons) / len(lons))
        max_r = max(haversine(centroid, points[i]) for i in cluster)
        summaries.append({"size": len(cluster), "centroid": centroid, "max_radius_km": max_r})
    return summaries


"""
## Usage

```python
if __name__ == "__main__":

    capitals = [
        (48.8566,   2.3522),   # Paris
        (51.5074,  -0.1278),   # London
        (52.5200,  13.4050),   # Berlin
        (41.9028,  12.4964),   # Rome
        (40.4168,  -3.7038),   # Madrid
        (59.9139,  10.7522),   # Oslo
        (55.6761,  12.5683),   # Copenhagen
        (52.2297,  21.0122),   # Warsaw
    ]

    clusters = cluster_points(capitals, radius_km=1500)
    summary = cluster_summary(capitals, clusters)

    print(f"Clustered {len(capitals)} capitals into {len(clusters)} groups (r=1500 km)\n")
    for i, s in enumerate(summary):
        lat, lon = s["centroid"]
        print(f"  Cluster {i+1}: {s['size']} cities, centroid ({lat:.2f}, {lon:.2f}), spread {s['max_radius_km']:.0f} km")
```
"""