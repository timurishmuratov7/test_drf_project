import pytest

@pytest.fixture
def input_value():
    return 4


def test_square_gifts_correct_value(input_value):
    subject = 2**2

    assert subject == input_value
