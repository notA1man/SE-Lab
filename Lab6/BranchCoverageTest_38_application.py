import pytest
from highway_toll import toll_for, toll_charge, pass_advice


# toll_charge: vehicle in EXEMPT (True / False)
@pytest.mark.parametrize("vehicle", ["ambulance", "fire_engine"])
def test_exempt_vehicles_pay_nothing(vehicle):
    assert toll_charge(vehicle, 4, True, False) == 0


def test_non_exempt_vehicle_pays_toll():
    assert toll_charge("truck", 4, False, False) == 250


# toll_for: axles < 2 (True / False)
@pytest.mark.parametrize("axles", [1, 0, -1])
def test_invalid_axles_raise(axles):
    with pytest.raises(ValueError, match="invalid axle count"):
        toll_for(axles, False, False)


# toll_for: axles in BASE_TOLL (True / False)
@pytest.mark.parametrize("axles, expected", [(2, 100), (3, 150), (4, 250), (5, 400), (8, 400)])
def test_base_toll_by_axles(axles, expected):
    assert toll_for(axles, False, False) == expected


# toll_for: is_peak (True / False)
def test_peak_adds_25_percent():
    assert toll_for(3, True, False) == 187.5


def test_off_peak_has_no_surcharge():
    assert toll_for(3, False, False) == 150


# toll_for: has_fastag (True / False) and axles == 2 (True / False)
def test_fastag_two_axles_ten_percent_off():
    assert toll_for(2, False, True) == 90.0


def test_fastag_more_axles_five_percent_off():
    assert toll_for(4, False, True) == 237.5


def test_no_fastag_no_discount():
    assert toll_for(2, False, False) == 100


def test_peak_and_fastag_combined():
    assert toll_for(2, True, True) == 112.5


# pass_advice: cost > price, cost == price, cost < price, loop with no trips
def test_pass_advice_buy_pass_when_cost_exceeds_price():
    assert pass_advice([(False, False)] * 3, 2, 250) == "buy_pass"


def test_pass_advice_either_when_cost_equals_price():
    assert pass_advice([(False, False)] * 3, 2, 300) == "either"


def test_pass_advice_pay_per_trip_when_cost_below_price():
    assert pass_advice([(False, False)] * 3, 2, 350) == "pay_per_trip"


def test_pass_advice_no_trips():
    assert pass_advice([], 2, 100) == "pay_per_trip"


def test_pass_advice_zero_cost_zero_price():
    assert pass_advice([], 2, 0) == "either"


def test_pass_advice_mixed_trips():
    trips = [(True, False), (False, True)]  # 125 + 90 = 215
    assert pass_advice(trips, 2, 215) == "either"
