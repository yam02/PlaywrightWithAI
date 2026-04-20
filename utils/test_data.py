"""Reusable test-data factories — unique users, reviewers, payment cards, etc."""
from __future__ import annotations

import uuid
from typing import TypedDict


class UserData(TypedDict):
    name: str
    email: str
    password: str
    dob_day: str
    dob_month: str
    dob_year: str
    first_name: str
    last_name: str
    company: str
    address: str
    address2: str
    country: str
    state: str
    city: str
    zipcode: str
    mobile: str


class ReviewerData(TypedDict):
    name: str
    email: str


def unique_token(length: int = 10) -> str:
    return uuid.uuid4().hex[:length]


def unique_user(**overrides) -> UserData:
    """Fresh signup-ready user with a unique email each call."""
    suffix = unique_token()
    user: UserData = {
        "name": f"pw_{suffix}",
        "email": f"pw_{suffix}@example.com",
        "password": "S3cr3tPw!",
        "dob_day": "10",
        "dob_month": "5",
        "dob_year": "1995",
        "first_name": "Test",
        "last_name": "Playwright",
        "company": "Anthropic",
        "address": "1 Market Street",
        "address2": "Suite 400",
        "country": "United States",
        "state": "California",
        "city": "San Francisco",
        "zipcode": "94105",
        "mobile": "+15555550123",
    }
    user.update(overrides)  # type: ignore[typeddict-item]
    return user


def unique_reviewer(**overrides) -> ReviewerData:
    """Fresh reviewer identity for product-review submissions."""
    suffix = unique_token()
    reviewer: ReviewerData = {
        "name": f"Reviewer {suffix}",
        "email": f"reviewer_{suffix}@example.com",
    }
    reviewer.update(overrides)  # type: ignore[typeddict-item]
    return reviewer
