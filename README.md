# HCM Rated Tracker

A simple Home Assistant integration to log books with a rating and generate lightweight recommendations.

**YAML is the source of truth** for the log at:

`/config/hcm_rated_tracker/books.yaml`

## books.yaml format

```yaml
entries:
  - title: The Hobbit
    author: J. R. R. Tolkien
    rating: 9
    date: 2026-01-05
```

- `date` is optional (defaults to today)
- `rating` must be 0–10

## Services

- `hcm_rated_tracker.log_item` (title, extra/author, rating)
- `hcm_rated_tracker.generate_recommendations`
- `hcm_rated_tracker.reload_books_yaml`
