from __future__ import annotations

import ckan.plugins.toolkit as tk

PREFIX = "ckanext.feedback."


def email_recipients() -> list[str]:
    raw = tk.config.get(PREFIX + "email_recipients", "")
    if not raw:
        return []
    return raw.split()


def recaptcha_site_key() -> str:
    return tk.config.get(PREFIX + "recaptcha_site_key", "")


def recaptcha_secret_key() -> str:
    return tk.config.get(PREFIX + "recaptcha_secret_key", "")


def subject_types() -> list[str]:
    raw = tk.config.get(
        PREFIX + "subject_types",
        "Citizen,Researcher,Developer,Government Employee,Other",
    )
    return [s.strip() for s in raw.split(",") if s.strip()]


def reasons() -> list[str]:
    raw = tk.config.get(
        PREFIX + "reasons",
        "Data Quality,Missing Data,Broken Link,Suggestion,Other",
    )
    return [s.strip() for s in raw.split(",") if s.strip()]
