import requests


BASE_URL = "https://oracleapex.com/ords/nbm_data/NBM_DBM"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 Firefox/149.0"
}


def get_customers():
    url = f"{BASE_URL}/Customers"

    response = requests.get(
        url,
        headers=HEADERS
    )

    response.raise_for_status()

    return response.json()


def create_customer(
    firstname,
    surname,
    cellphone,
    email
):
    url = f"{BASE_URL}/Customers"

    payload = {
        "F_NAME": firstname,
        "S_NAME": surname,
        "E_EMAIL": email,
        "C_PHONE": cellphone
    }

    print()
    print("==============================================")
    print("        ORACLE CUSTOMER CREATION")
    print("==============================================")
    print("URL:", url)
    print("Payload:", payload)
    print()

    response = requests.post(
        url,
        json=payload,
        headers=HEADERS
    )

    print("Oracle status code:", response.status_code)
    print("Oracle response:", response.text)
    print()

    if response.status_code >= 400:

        print("==============================================")
        print("        ORACLE CUSTOMER CREATION FAILED")
        print("==============================================")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        print("Payload:", payload)
        print("==============================================")
        print()

    response.raise_for_status()

    if response.text:

        try:

            data = response.json()

            if data:
                return data

        except ValueError:

            pass

    customers = get_customers()

    items = customers.get(
        "items",
        []
    )

    for customer in items:

        if (
            str(
                customer.get(
                    "FIRSTNAME",
                    customer.get(
                        "firstname",
                        ""
                    )
                )
            ).strip().lower()
            ==
            str(firstname).strip().lower()

            and

            str(
                customer.get(
                    "SURNAME",
                    customer.get(
                        "surname",
                        ""
                    )
                )
            ).strip().lower()
            ==
            str(surname).strip().lower()

            and

            str(
                customer.get(
                    "CELLPHONE",
                    customer.get(
                        "cellphone",
                        ""
                    )
                )
            ).strip()
            ==
            str(cellphone).strip()

            and

            str(
                customer.get(
                    "EMAIL",
                    customer.get(
                        "email",
                        ""
                    )
                )
            ).strip().lower()
            ==
            str(email).strip().lower()
        ):

            return customer

    return None

def get_services():
    url = f"{BASE_URL}/Services"

    response = requests.get(
        url,
        headers=HEADERS
    )

    response.raise_for_status()

    return response.json()


def get_bookings():
    url = f"{BASE_URL}/Bookings"

    response = requests.get(
        url,
        headers=HEADERS
    )

    response.raise_for_status()

    return response.json()


def create_booking(
    cust_id,
    serve_id,
    booking_date,
    status="Pending",
    calcom_booking_id=None
):
    url = f"{BASE_URL}/Bookings"

    if booking_date:
        if booking_date.endswith("Z"):
            booking_date = booking_date.replace(
                "Z",
                ".000+00:00"
            )

        elif "." not in booking_date:
            if "+" in booking_date:
                booking_date = booking_date.replace(
                    "+00:00",
                    ".000+00:00"
                )

    if calcom_booking_id is not None:
        calcom_booking_id = str(calcom_booking_id)

    payload = {
        "C_ID": int(cust_id),
        "S_ID": int(serve_id),
        "B_DATE": booking_date,
        "S_STATUS": str(status),
        "CBI_BOOKING_ID": calcom_booking_id
    }

    response = requests.post(
        url,
        json=payload,
        headers=HEADERS
    )

    if response.status_code >= 400:
        print()
        print("==============================================")
        print("          ORACLE BOOKING CREATION FAILED")
        print("==============================================")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        print("Payload:", payload)
        print()

    response.raise_for_status()

    if response.text:
        try:
            return response.json()
        except ValueError:
            pass

    return None

def update_booking(
    booking_id,
    cust_id,
    serve_id,
    booking_date,
    status,
    calcom_booking_id=None
):
    url = f"{BASE_URL}/Bookings"

    if booking_date:
        if booking_date.endswith("Z"):
            booking_date = booking_date.replace(
                "Z",
                ".000+00:00"
            )

        elif "." not in booking_date:
            if "+" in booking_date:
                booking_date = booking_date.replace(
                    "+00:00",
                    ".000+00:00"
                )

    if calcom_booking_id is not None:
        calcom_booking_id = str(calcom_booking_id)

    update_headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 Firefox/149.0",
        "B_ID": str(int(booking_id)),
        "C_ID": str(int(cust_id)),
        "S_ID": str(int(serve_id)),
        "B_DATE": str(booking_date),
        "S_STATUS": str(status),
        "CBI_BOOKING_ID": (
            str(calcom_booking_id)
            if calcom_booking_id is not None
            else ""
        )
    }

    print()
    print("Sending Oracle UPDATE request...")
    print("Headers:", update_headers)
    print()

    response = requests.put(
        url,
        headers=update_headers
    )

    print("Oracle response status:", response.status_code)
    print("Oracle response:", response.text)

    if response.status_code >= 400:
        print()
        print("Oracle UPDATE BOOKING failed")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        print("Headers:", update_headers)
        print()

    response.raise_for_status()

    if response.text:
        try:
            return response.json()
        except ValueError:
            return {
                "success": True,
                "message": response.text
            }

    return {
        "success": True
    }


def get_payments():
    url = f"{BASE_URL}/Payments"

    response = requests.get(
        url,
        headers=HEADERS
    )

    response.raise_for_status()

    return response.json()


def create_payment(
    booking_id,
    amount,
    status="Pending",
    yoco_payment_id=None
):
    url = f"{BASE_URL}/Payments"

    payload = {
        "B_ID": int(booking_id),
        "A_AMOUNT": amount,
        "S_STATUS": str(status),
        "Y_PAYMENT_ID": 
            str(yoco_payment_id)
            if yoco_payment_id is not None
            else None
                }

    response = requests.post(
        url,
        json=payload,
        headers=HEADERS
    )

    if response.status_code >= 400:
        print()
        print("==============================================")
        print("          ORACLE PAYMENT CREATION FAILED")
        print("==============================================")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        print("Payload:", payload)
        print()

    response.raise_for_status()

    if response.text:
        try:
            return response.json()
        except ValueError:
            pass

    return None


def display_customers():
    data = get_customers()

    print()
    print("==============================================")
    print("              CUSTOMERS")
    print("==============================================")

    items = data.get("items", [])

    if not items:
        print("No customers found.")
        return

    for customer in items:
        print(
            f"ID: {customer.get('CUST_ID')} | "
            f"Name: {customer.get('FIRSTNAME')} "
            f"{customer.get('SURNAME')} | "
            f"Phone: {customer.get('CELLPHONE')} | "
            f"Email: {customer.get('EMAIL')}"
        )


def display_services():
    data = get_services()

    print()
    print("==============================================")
    print("               SERVICES")
    print("==============================================")

    items = data.get("items", [])

    if not items:
        print("No services found.")
        return

    for service in items:
        print(
            f"ID: {service.get('SERVE_ID')} | "
            f"Service: {service.get('SERVICE_NAME')} | "
            f"Price: R{service.get('PRICE')} | "
            f"Deposit: R{service.get('DEPOSIT')}"
        )


def display_bookings():
    data = get_bookings()

    print()
    print("==============================================")
    print("               BOOKINGS")
    print("==============================================")

    items = data.get("items", [])

    if not items:
        print("No bookings found.")
        return

    for booking in items:
        print(
            f"Booking ID: {booking.get('BOOKING_ID')} | "
            f"Customer ID: {booking.get('CUST_ID')} | "
            f"Service ID: {booking.get('SERVE_ID')} | "
            f"Date: {booking.get('BOOKING_DATE')} | "
            f"Status: {booking.get('STATUS')} | "
            f"Cal.com ID: {booking.get('CALCOM_BOOKING_ID')}"
        )


def display_payments():
    data = get_payments()

    print()
    print("==============================================")
    print("               PAYMENTS")
    print("==============================================")

    items = data.get("items", [])

    if not items:
        print("No payments found.")
        return

    for payment in items:
        print(
            f"Payment ID: {payment.get('PAY_ID')} | "
            f"Booking ID: {payment.get('BOOKING_ID')} | "
            f"Amount: R{payment.get('AMOUNT')} | "
            f"Status: {payment.get('STATUS')}"
        )


if __name__ == "__main__":

    print()
    print("==============================================")
    print("          NAILS BY MIKA - ORACLE API")
    print("==============================================")

    print()
    print("Available functions:")
    print("GET  Customers")
    print("POST Customers")
    print("GET  Services")
    print("GET  Bookings")
    print("POST Bookings")
    print("PUT  Bookings")
    print("GET  Payments")
    print("POST Payments")
    print()

