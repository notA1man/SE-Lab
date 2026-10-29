import pytest
from highway_toll import toll_for, toll_charge, pass_advice


def test_ambulance_is_exempt():
    assert toll_charge("ambulance", 2, False, False) == 0


def test_two_axle_base_toll():
    assert toll_for(2, False, False) == 100


def test_invalid_axle_count_raises():
    with pytest.raises(ValueError):
        toll_for(1, False, False)


def test_three_axle_base_toll():
    assert toll_for(3, False, False) == 150


def test_many_axles_use_default_base():
    assert toll_for(5, False, False) == 400


def test_peak_surcharge():
    assert toll_for(2, True, False) == 125.0


def test_fastag_discount_two_axles():
    assert toll_for(2, False, True) == 90.0


def test_fastag_discount_more_axles():
    assert toll_for(3, False, True) == 142.5


def test_regular_vehicle_is_charged():
    assert toll_charge("car", 2, False, False) == 100


def test_pass_advice_buy_pass():
    trips = [(False, False), (False, False)]
    assert pass_advice(trips, 2, 150) == "buy_pass"


def test_pass_advice_either():
    trips = [(False, False), (False, False)]
    assert pass_advice(trips, 2, 200) == "either"


def test_pass_advice_pay_per_trip():
    trips = [(False, False), (False, False)]
    assert pass_advice(trips, 2, 300) == "pay_per_trip"
