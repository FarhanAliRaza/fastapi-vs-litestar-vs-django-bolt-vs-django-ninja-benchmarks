"""User model for Django benchmark."""

from __future__ import annotations

from django.db import models


class BenchmarkUser(models.Model):
    """User model for benchmark tests."""

    username = models.CharField(max_length=50, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "benchmark_users"
