import allure
import requests
import pytest
from core.schemas.booking_schema import BOOKING_SCHEMA
import jsonschema


@allure.feature("Test Booking")
@allure.story("Test create booking")
def test_create_booking(
        api_client,
        generate_random_booking_data
):
    response_json = api_client.create_booking(booking_data=generate_random_booking_data)
    print(response_json)
    assert isinstance(response_json, dict)
    assert response_json["booking"] == generate_random_booking_data
    assert "bookingid" in response_json
    jsonschema.validate(response_json, BOOKING_SCHEMA)
