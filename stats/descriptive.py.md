# Descriptive Statistics

Pure-Python descriptive statistics used to summarise distance matrices
produced by the [Haversine module](../geo/haversine.py).

---

## Measures of Central Tendency

### Mean

$$
\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i
$$

**`mean(data)`**

- `data` *(list[float])* — non-empty list of numeric values

*Returns* `float` — arithmetic mean

```python xp-source
import math

def mean(data: list[float]) -> float:
    if not data:
        raise ValueError("data must be non-empty")
    return sum(data) / len(data)
```

### Median

The middle value when data is sorted. For even-length sequences the
average of the two middle values is returned.

**`median(data)`**

- `data` *(list[float])* — list of numeric values

*Returns* `float` — median value

```python xp-source
def median(data: list[float]) -> float:
    s = sorted(data)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2
```

## Measures of Spread

### Variance and Standard Deviation

Population variance:

$$
\sigma^2 = \frac{1}{n} \sum_{i=1}^{n} (x_i - \bar{x})^2
$$

Sample variance uses $n - 1$ (Bessel's correction):

$$
s^2 = \frac{1}{n-1} \sum_{i=1}^{n} (x_i - \bar{x})^2
$$

**`variance(data, sample=True)`**

- `data` *(list[float])* — list of at least 2 numeric values
- `sample` *(bool)* — if `True` uses Bessel's correction, otherwise population variance

*Returns* `float` — variance

```python xp-source
def variance(data: list[float], sample: bool = True) -> float:
    n = len(data)
    if n < 2:
        raise ValueError("need at least 2 values")
    m = mean(data)
    denom = n - 1 if sample else n
    return sum((x - m) ** 2 for x in data) / denom
```

**`std(data, sample=True)`**

- `data` *(list[float])* — list of at least 2 numeric values
- `sample` *(bool)* — passed through to `variance`

*Returns* `float` — standard deviation

```python xp-source
def std(data: list[float], sample: bool = True) -> float:
    return math.sqrt(variance(data, sample))
```

## Summary

Produce a compact summary dict for a flat list of values.
Used by the [pipeline](pipeline.py?id=run-pipeline) to report distance statistics.

**`summary(data, label="data")`**

- `data` *(list[float])* — list of numeric values
- `label` *(str)* — descriptive name shown in output

*Returns* `dict` — keys `label`, `n`, `min`, `max`, `mean`, `median`, `std`

```python xp-source
def summary(data: list[float], label: str = "data") -> dict:
    return {
        "label":  label,
        "n":      len(data),
        "min":    min(data),
        "max":    max(data),
        "mean":   mean(data),
        "median": median(data),
        "std":    std(data),
    }
```

**`print_summary(s)`**

- `s` *(dict)* — summary dict from `summary`

```python xp-source
def print_summary(s: dict) -> None:
    print(f"\n── {s['label']} (n={s['n']}) ──")
    print(f"  min     {s['min']:>10.2f}")
    print(f"  max     {s['max']:>10.2f}")
    print(f"  mean    {s['mean']:>10.2f}")
    print(f"  median  {s['median']:>10.2f}")
    print(f"  std     {s['std']:>10.2f}")
```

## Usage

```python
if __name__ == "__main__":
    sample_data = [120.5, 340.2, 89.1, 560.8, 230.4, 415.3, 178.9, 302.7]
    print_summary(summary(sample_data, "sample distances (km)"))
```