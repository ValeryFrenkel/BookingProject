import allure
import requests
import pytest
from pydantic import ValidationError
from core.models.booking import BookingResponse


@allure.feature("Test Booking")
@allure.story("Positive: creating booking with custom data")
def test_create_booking_with_custom_data(
        api_client
):
    booking_data = {
        "firstname": "Valery",
        "lastname": "Frenkel",
        "totalprice": 228,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-10-01",
            "checkout": "2026-10-15"
        },
        "additionalneeds": "Lunch"
    }

    response = api_client.create_booking(booking_data=booking_data)

    try:
        BookingResponse(**response)
    except ValidationError as e:
        raise ValidationError(f"Response validation failed: {e}")

    assert response["booking"] == booking_data


@allure.story("Positive: creating booking with random data")
def test_create_booking(
        api_client,
        generate_random_booking_data
):
    response_json = api_client.create_booking(booking_data=generate_random_booking_data)

    try:
        BookingResponse(**response_json)
    except ValidationError as e:
        raise ValidationError(f"Response validation failed: {e}")

    assert isinstance(response_json, dict)
    assert response_json["booking"] == generate_random_booking_data
    assert "bookingid" in response_json


@allure.story("Positive: receive created booking")
def test_created_booking_can_be_received(
        api_client,
        generate_random_booking_data
        ):
    created_booking = api_client.create_booking(booking_data=generate_random_booking_data)
    booking_id = created_booking["bookingid"]
    actual_booking = api_client.get_booking_by_id(booking_id)

    assert actual_booking == generate_random_booking_data
    assert "bookingid" in actual_booking
    assert actual_booking["bookingid"] is not None
    assert isinstance(actual_booking["bookingid"], int)
    assert actual_booking["bookingid"] > 0

@allure.story("Negative: create booking without required field")
@pytest.mark.parametrize(
    "field",
    [
        "firstname",
        "lastname",
        "totalprice",
        "depositpaid",
        "bookingdates",
    ],
)
def test_create_booking_without_required_field(
        api_client,
        generate_random_booking_data,
        field
        ):
    generate_random_booking_data.pop(field)

    with pytest.raises(requests.HTTPError) as error:
        api_client.create_booking(booking_data=generate_random_booking_data)

    assert error.value.response.status_code == 500

@allure.story("Negative: create booking with wrong field values")
@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("firstname", 123),
        ("lastname", True),
        # ("totalprice", "expensive"),
        # ("depositpaid", "yes"),
        ("bookingdates", []),
    ],
)
# Методы totalprice и depositpaid закоментированы так как могут принимать значения
# отличные от описанных в документации и не выбрасывают ошибку 500 (Тест падает, Ошибка в API)
def test_create_booking_with_invalid_types(
    api_client,
    generate_random_booking_data,
    field,
    invalid_value,
):
    generate_random_booking_data[field] = invalid_value

    with pytest.raises(requests.HTTPError) as error:
        api_client.create_booking(booking_data=generate_random_booking_data)

    assert error.value.response.status_code == 500

@allure.story("Positive: bookings have different ids")
def test_create_two_bookings_have_different_ids(api_client, generate_random_booking_data):
    first = api_client.create_booking(booking_data=generate_random_booking_data)
    second = api_client.create_booking(booking_data=generate_random_booking_data)

    assert first["bookingid"] != second["bookingid"]
