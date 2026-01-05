# HCM Rated Tracker (Book Tracker)

A small Home Assistant custom integration that lets you log books with a 1–10 rating and shows:
- Draft fields (Title, Author, Rating) you can edit directly in the dashboard
- Buttons to Save (log the book) and Recommend (generate suggestions)
- A Log text entity (latest entries)
- A Recommendations text entity

## Editable data file (recommended)
Create/edit:

`/config/hcm_rated_tracker/books.yaml`

Example:

```yaml
entries:
  - date: 2026-01-05
    title: Sharp Objects
    author: Gillian Flynn
    rating: 8
```

If `books.yaml` exists it is treated as the source of truth on startup and on reload.

## Services
- `hcm_rated_tracker.log_item` — Log a book (title, extra/author, rating)
- `hcm_rated_tracker.generate_recommendations` — Regenerate suggestions
- `hcm_rated_tracker.reload_books_yaml` — Reload `/config/hcm_rated_tracker/books.yaml`

## Notes
- If `books.yaml` exists, saving/logging will also write back to it (keeps it in sync).
