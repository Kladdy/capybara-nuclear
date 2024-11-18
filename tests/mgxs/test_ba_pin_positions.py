from capybara_nuclear.mgxs.openmc import ba_pin_positions
import pytest
import os

def test_ba_pin_positions(request: pytest.FixtureRequest):
    ba_pin_positions.visualize(10, os.path.join(os.path.dirname(request.path), 'ba_pin_positions'))
