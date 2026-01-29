"""
Example code generated in LITE mode.

This file demonstrates what the kit produces in LITE mode:
- OOP + strong typing (always)
- No automatic validators
- Direct, pragmatic output
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol


class Shape(Protocol):
    """Protocol for geometric shapes."""

    def area(self) -> float:
        """Return the shape area."""
        ...

    def perimeter(self) -> float:
        """Return the shape perimeter."""
        ...


@dataclass
class Circle:
    """A circle with basic geometric operations."""

    radius: float

    def __post_init__(self) -> None:
        if self.radius <= 0:
            raise ValueError("radius must be positive")

    def area(self) -> float:
        """Area: pi * r^2."""
        return math.pi * (self.radius**2)

    def perimeter(self) -> float:
        """Circumference: 2 * pi * r."""
        return 2 * math.pi * self.radius

    def diameter(self) -> float:
        """Diameter: 2 * r."""
        return 2 * self.radius


@dataclass
class Rectangle:
    """A rectangle with basic geometric operations."""

    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("dimensions must be positive")

    def area(self) -> float:
        """Area: width * height."""
        return self.width * self.height

    def perimeter(self) -> float:
        """Perimeter: 2 * (width + height)."""
        return 2 * (self.width + self.height)

    def is_square(self) -> bool:
        """Return True if width and height are effectively equal."""
        return math.isclose(self.width, self.height, rel_tol=1e-9, abs_tol=0.0)


class GeometryCalculator:
    """Utility functions for working with shapes."""

    @staticmethod
    def compare_areas(shape1: Shape, shape2: Shape) -> tuple[Shape, Shape]:
        """Return (larger, smaller) by area."""
        if shape1.area() >= shape2.area():
            return shape1, shape2
        return shape2, shape1

    @staticmethod
    def total_area(shapes: list[Shape]) -> float:
        """Sum the area of multiple shapes."""
        return sum(shape.area() for shape in shapes)


if __name__ == "__main__":
    circle = Circle(radius=5.0)
    rectangle = Rectangle(width=4.0, height=6.0)

    print(f"Circle area: {circle.area():.2f}")
    print(f"Rectangle area: {rectangle.area():.2f}")

    larger, _smaller = GeometryCalculator.compare_areas(circle, rectangle)
    print(f"Larger shape area: {larger.area():.2f}")
