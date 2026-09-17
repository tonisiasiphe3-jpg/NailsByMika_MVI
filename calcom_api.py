import os
import requests
from datetime import datetime, timezone


BASE_URL = "https://api.cal.com"

API_KEY = os.getenv("CAL_API_KEY")

USERNAME = "nails-by-mika"
EVENT_SLUG = "120min"

TIMEZONE = "Africa/Johannesburg"


EVENT_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "cal-api-version": "2024-06-14",
    "Accept": "application/json"
}

SLOTS_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "cal-api-version": "2024-09-04",
    "Accept": "application/json"
}

BOOKING_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "cal-api-version": "2026-02-25",
    "Content-Type": "application/json",
    "Accept": "application/json"
}


def check_api_key():

    if not API_KEY:

        return False

    return True


def get_event_type():

    url = f"{BASE_URL}/v2/event-types"

    params = {
        "username": USERNAME,
        "eventSlug": EVENT_SLUG
    }

    try:

        response = requests.get(
            url,
            headers=EVENT_HEADERS,
            params=params
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException:

        return None


def get_event_from_response(response_data):

    if response_data is None:

        return None

    data = response_data.get(
        "data"
    )

    if isinstance(data, list):

        if len(data) > 0:

            return data[0]

    elif isinstance(data, dict):

        return data

    return None


def display_event_type(event):

    if event is None:

        return

    return


def get_available_slots(
    event_type_id,
    booking_date
):

    url = f"{BASE_URL}/v2/slots"

    params = {
        "eventTypeId": event_type_id,
        "start": booking_date,
        "end": booking_date,
        "timeZone": TIMEZONE
    }

    try:

        response = requests.get(
            url,
            headers=SLOTS_HEADERS,
            params=params
        )

        response.raise_for_status()

        response_data = response.json()

        if isinstance(
            response_data.get("data"),
            dict
        ):

            filtered_data = {}

            for date, slots in response_data[
                "data"
            ].items():

                if date == booking_date:

                    filtered_data[date] = slots

            response_data["data"] = filtered_data

        return response_data

    except requests.exceptions.RequestException:

        return None


def display_available_slots(slots_data):

    if not slots_data:

        return

    data = slots_data.get(
        "data",
        {}
    )

    if not data:

        return

    return


def get_first_available_slot(
    slots_data
):

    if not slots_data:

        return None

    data = slots_data.get(
        "data",
        {}
    )

    for date, slots in data.items():

        if slots:

            return slots[0]

    return None


def create_booking(
    event_type_id,
    start_time,
    firstname,
    surname,
    cellphone,
    email
):
    url = f"{BASE_URL}/v2/bookings"

    try:
        local_datetime = datetime.fromisoformat(
            start_time.replace("Z", "+00:00")
        )

        utc_datetime = local_datetime.astimezone(
            timezone.utc
        )

        utc_start_time = (
            utc_datetime
            .isoformat()
            .replace("+00:00", "Z")
        )

    except Exception as error:
        return {
            "success": False,
            "error_type": "datetime_conversion",
            "message": str(error)
        }

    customer_name = f"{firstname} {surname}".strip()

    phone = str(cellphone).strip()

    if phone.startswith("0"):
        phone = "+27" + phone[1:]

    elif not phone.startswith("+"):
        phone = "+27" + phone

    if not email or not str(email).strip():
        return {
            "success": False,
            "error_type": "missing_email",
            "message": "Customer email is required"
        }

    email = str(email).strip().lower()

    payload = {
    "start": utc_start_time,
    "eventTypeId": int(event_type_id),

    "attendee": {
        "name": customer_name,
        "email": email,
        "timeZone": TIMEZONE,
        "phoneNumber": phone,
        "language": "en"
    },

    "bookingFieldsResponses": {
        "Last-Name": surname
    }
}

    print()
    print("==============================================")
    print("        CAL.COM BOOKING REQUEST")
    print("==============================================")
    print("URL:", url)
    print("Start:", utc_start_time)
    print("Event Type ID:", event_type_id)
    print("Customer:", customer_name)
    print("Email:", email)
    print("Phone:", phone)
    print("Payload:", payload)
    print()

    try:

        response = requests.post(
            url,
            headers=BOOKING_HEADERS,
            json=payload
        )

        print(
            "Cal.com response status:",
            response.status_code
        )

        print(
            "Cal.com response:",
            response.text
        )

        print()

        if response.status_code in [200, 201]:

            response_data = response.json()

            return {
                "success": True,
                "data": response_data.get(
                    "data",
                    {}
                )
            }

        try:
            error_data = response.json()

        except ValueError:
            error_data = {
                "raw_response": response.text
            }

        return {
            "success": False,
            "status_code": response.status_code,
            "error": error_data
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "error_type": "request_error",
            "message": str(error)
        }