# Explicode Demo

A Python toolkit that computes great-circle distances between geographic coordinates, clusters locations by proximity, and summarises the results with descriptive statistics.

Built with [Explicode](https://explicode.com) — write Markdown inside your code comments to create beautiful documentation automatically. See the documentation [here](https://www.npmjs.com/package/explicode?activeTab=readme).

---

## Project Overview

- [Haversine distance](geo/haversine.py) — great-circle distance between two coordinates
- [Clustering](geo/clustering.py) — group points by proximity
- [Statistics](stats/descriptive.py) — mean, variance, standard deviation
- [Pipeline](stats/pipeline.py) — run the full analysis end to end

## Quick start

```bash
python stats/pipeline.py
```

## How it fits together

The [pipeline](stats/pipeline.py?id=run-pipeline) loads a set of cities, computes [pairwise distances](geo/haversine.py?id=pairwise-distances) using the Haversine formula, then feeds the distance matrix into the [clustering](geo/clustering.py?id=cluster-points) step. Summary [statistics](stats/descriptive.py?id=summary) are printed at the end.

See the [math behind Haversine](geo/haversine.py?id=the-formula) for the derivation.

## Sample output

```text
Cities: New York, London, Tokyo, Sydney, São Paulo, Cairo, Mumbai, Mexico City, Lagos, Beijing

── all pairwise distances (km) (n=45) ──
  min        2089.39
  max       18537.21
  mean       9883.82
  median     9558.56
  std        4066.19

Clusters (radius = 8,000 km): 3 group(s)
  [1] New York, London, São Paulo, Mexico City
       centroid (22.0°, -55.0°)  spread 5700 km
  [2] Tokyo, Sydney, Mumbai, Beijing
       centroid (15.2°, 120.0°)  spread 6377 km
  [3] Cairo, Lagos
       centroid (18.3°, 17.3°)  spread 1997 km

Longest route:  Tokyo ↔ São Paulo  (18,537 km)
Shortest route: Tokyo ↔ Beijing  (2,089 km)
```


## Changelog

See updates [here](CHANGELOG.md).

---

![Globe](./assets/globe.webp)