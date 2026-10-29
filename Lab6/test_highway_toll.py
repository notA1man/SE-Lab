import pytest
from highway_toll import toll_for, toll_charge, pass_advice

#Example test cases:
def test_ambulance_is_exempt():
    assert toll_charge("ambulance", 2, False, False) == 0

def test_two_axle_base_toll():
    assert toll_for(2, False, False) == 100

#Write the rest of the test cases so that the code is 90- 100% covered.
