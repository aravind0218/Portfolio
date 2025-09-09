# -*- coding: utf8 -*-

"""Utilities for version comparison."""

from __future__ import annotations

__all__ = ['Version', 'compare', 'sort']

import collections.abc
import functools
import re
import typing

import packaging.version


NUMBER: typing.Final[re.Pattern[str]] = re.compile(r'([0-9]+)')


@functools.total_ordering
class Version:
    """Wrapper for versions strings that can be used for comparison."""

    def __init__(self, value: str | Version | None) -> None:
        """Initialize new instance of a :class:`~Version`."""
        self.raw: typing.Final[str] = str(value or '').strip()

    @functools.cached_property
    def parts(self) -> tuple[str | int, ...]:  # noqa: D401
        """
        Format-independent representation of a version.

        Might be used for a general comparison when version is not compatible with semver specifics.
        """
        return tuple(
            int(part) if (index % 2) else str(part)
            for index, part in enumerate(NUMBER.split(self.raw))
        )

    @functools.cached_property
    def version(self) -> packaging.version.Version | None:  # noqa: D401
        """Semver compatible version representation."""
        try:
            return packaging.version.Version(self.raw)
        except packaging.version.InvalidVersion:
            return None

    def __eq__(self, other: typing.Any) -> bool:
        """Check if instances are equal."""
        if isinstance(other, Version):
            return (self.raw == other.raw) or (self.version == other.version)
        return NotImplemented

    def __hash__(self) -> int:
        """Compute a hash of an instance."""
        return hash(self.raw)

    def __lt__(self, other: typing.Any) -> bool:
        """Check if current instance is less than other instance."""
        if isinstance(other, Version):
            if (self.version is not None) and (other.version is not None):
                return self.version < other.version
            return self.parts < other.parts
        return NotImplemented

    def __repr__(self) -> str:
        """Return string representation of an instance."""
        return f'{type(self).__name__}({self.raw!r})'

    def __str__(self) -> str:
        """Return string representation of an instance."""
        return self.raw


def as_version(value: str | Version) -> Version:
    """Make sure that :code:`value` is :class:`~Version`."""
    if isinstance(value, Version):
        return value
    return Version(value)


def compare(left: str | Version, right: str | Version) -> int:
    """Compare two versions."""
    left = as_version(left)
    right = as_version(right)
    if left == right:
        return 0
    if left < right:
        return -1
    return 1


@typing.overload
def sort(
        values: collections.abc.Iterable[str | Version],
        reverse: bool = ...,
        *,
        keep_versions: typing.Literal[False] = ...,
        unique: bool = ...,
) -> list[str]:
    """Sort sequence of versions."""


@typing.overload
def sort(
        values: collections.abc.Iterable[str | Version],
        reverse: bool = ...,
        *,
        keep_versions: typing.Literal[True],
        unique: bool = ...,
) -> list[Version]:
    """Sort sequence of versions."""


def sort(
        values: collections.abc.Iterable[str | Version],
        reverse: bool = False,
        *,
        keep_versions: bool = False,
        unique: bool = False,
) -> list[Version] | list[str]:
    """
    Sort sequence of versions.

    :param values: Versions to sort.
    :param reverse: Perform a reversed sorting (from largest to smallest).
    :param keep_versions: Return list of versions instead of list of strings.
    :param unique: Remove repeating versions from the output.
    :return: List of sorted versions.
    """
    if unique:
        values = set(values)

    result: list[Version] = sorted(map(as_version, values), reverse=reverse)

    if keep_versions:
        return result
    return list(map(str, result))
