# ckanext-feedback

Dataset feedback and star rating extension for CKAN 2.11+.

Provides a 5-star rating widget and a feedback submission form for datasets.
At the moment feedback is only visible to sysadmins in the CKAN admin panel — it
is never displayed publicly on dataset pages. Star ratings (average + count) are
displayed publicly.

## Installation

```bash
pip install -e git+https://github.com/TkTech/ckanext-feedback.git#egg=ckanext-feedback
```

Add `feedback` to `ckan.plugins` in your CKAN config, then run the database
migration:

```bash
ckan -c ckan.ini db upgrade -p feedback
```

## Configuration

| Setting | Default | Purpose |
|---------|---------|---------|
| `ckanext.feedback.email_recipients` | `""` | Space-separated emails notified on new feedback |
| `ckanext.feedback.recaptcha_site_key` | `""` | reCAPTCHA v2 site key (empty = disabled) |
| `ckanext.feedback.recaptcha_secret_key` | `""` | reCAPTCHA v2 secret key |
| `ckanext.feedback.subject_types` | `"Citizen,Researcher,Developer,Government Employee,Other"` | Comma-separated "I am a" options |
| `ckanext.feedback.reasons` | `"Data Quality,Missing Data,Broken Link,Suggestion,Other"` | Comma-separated "Reason" options |

## Template Integration

This extension provides snippets but does **not** automatically inject them
into dataset pages. Your theme is responsible for placing them where
appropriate.

### Star Rating Widget

Add to your dataset sidebar (e.g. in `package/read_base.html`):

```jinja2
{% snippet "feedback/snippets/rating_widget.html", pkg=pkg %}
```

### Feedback Form

Add to your dataset page (e.g. in `package/read.html`):

```jinja2
{% snippet "feedback/snippets/feedback_form.html", pkg=pkg %}
```

### Admin Panel

The admin panel tab is registered automatically. Sysadmins can view and
delete feedback submissions at `/ckan-admin/feedback`.

## Template Helpers

Available in templates via `h.*`:

- `h.feedback_rating_avg(package_id)` — returns `{"average": float, "count": int}`
- `h.feedback_user_rating(package_id)` — returns the current visitor's rating (int or None)
- `h.feedback_recaptcha_site_key()` — returns the configured site key (empty string if disabled)
- `h.feedback_subject_types()` — returns list of "I am a" options
- `h.feedback_reasons()` — returns list of "Reason" options

## i18n

English and French translations are included. More translations are always
welcome!