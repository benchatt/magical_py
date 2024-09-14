import pytest
import random

@pytest.fixture(autouse=True)
def seed():
    random.seed(90210)
