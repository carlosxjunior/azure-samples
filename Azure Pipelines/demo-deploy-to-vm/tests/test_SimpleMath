import pytest
from src.simple_math import SimpleMath

@pytest.mark.parametrize(
        "a, b, expected", 
        [
            (1, 2, 3),
            (-1, -1, -2),
            (0, 5, 5),
            (3.5, 2.5, 6.0)
        ]
    )
def test_add(a, b, expected):
    """Test the add function of SimpleMath."""
    assert SimpleMath.add(a, b) == expected

@pytest.mark.parametrize(
        "a, b, expected", 
        [
            (1, 2, 2),
            (-1, -1, 1),
            (0, 5, 0),
            (3.5, 2, 7.0)
        ]
    )
def test_multiply(a, b, expected):
    """Test the multiply function of SimpleMath."""
    assert SimpleMath.multiply(a, b) == expected