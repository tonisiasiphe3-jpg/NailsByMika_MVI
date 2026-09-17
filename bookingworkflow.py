from oracle_api import (
    get_customers,
    create_customer,
    get_services
)

from calcom_api import (
    check_api_key,
    get_event_type,
    get_event_from_response,
    get_available_slots
)

from yoco import create_checkout


def find_customer(
    firstname,
    surname,
    cellphone,
    email
):
    customers_data = get_customers()
    customers = customers_data.get("items", [])

    firstname_clean = firstname.strip().lower()
    surname_clean = surname.strip().lower()
    cellphone_clean = str(cellphone).strip()
    email_clean = email.strip().lower()

    for customer in customers:
        db_firstname = str(
            customer.get("firstname", "")
        ).strip().lower()

        db_surname = str(
            customer.get("surname", "")
        ).strip().lower()

        db_cellphone = str(
            customer.get("cellphone", "")
        ).strip()

        db_email = str(
            customer.get("email", "")
        ).strip().lower()

        if (
            db_firstname == firstname_clean
            and db_surname == surname_clean
            and db_cellphone == cellphone_clean
            and db_email == email_clean
        ):
            return customer

    return None


def booking_workflow():

    if not check_api_key():
        print("ERROR: Cal.com API key was not found.")
        return

    print()
    print("NAILS BY MIKA BOOKING SYSTEM")
    print()

    firstname = input(
        "Enter first name: "
    ).strip()

    surname = input(
        "Enter surname: "
    ).strip()

    email = input(
        "Enter email address: "
    ).strip().lower()

    cellphone = input(
        "Enter cellphone number: "
    ).strip()

    if not firstname:
        print("ERROR: First name is required.")
        return

    if not surname:
        print("ERROR: Surname is required.")
        return

    if not email:
        print("ERROR: Email is required.")
        return

    if not cellphone:
        print("ERROR: Cellphone number is required.")
        return

    existing_customer = find_customer(
        firstname,
        surname,
        cellphone,
        email
    )

    if existing_customer:
        customer = existing_customer
        cust_id = customer.get("cust_id")

    else:
        customer = create_customer(
            firstname,
            surname,
            email,
            cellphone
        )

        if not customer:
            print(
                "ERROR: Customer could not be created."
            )
            return

        cust_id = customer.get("cust_id")

    if not cust_id:
        print(
            "ERROR: Customer ID could not be found."
        )
        return

    services_data = get_services()

    services = services_data.get(
        "items",
        []
    )

    if not services:
        print(
            "ERROR: No services were found."
        )
        return

    print()
    print("AVAILABLE SERVICES")
    print()

    for service in services:
        print(
            f"ID: {service.get('serve_id')} | "
            f"Service: {service.get('service_name')} | "
            f"Price: R{service.get('price')} | "
            f"Deposit: R{service.get('deposit')}"
        )

    try:
        serve_id = int(
            input(
                "\nEnter service ID: "
            ).strip()
        )

    except ValueError:
        print(
            "ERROR: Invalid service ID."
        )
        return

    selected_service = None

    for service in services:
        try:
            service_id = int(
                service.get("serve_id")
            )

        except (
            TypeError,
            ValueError
        ):
            continue

        if service_id == serve_id:
            selected_service = service
            break

    if not selected_service:
        print(
            "ERROR: Service not found."
        )
        return

    service_name = selected_service.get(
        "service_name"
    )

    service_price = float(
        selected_service.get(
            "price",
            0
        )
    )

    deposit = float(
        selected_service.get(
            "deposit",
            0
        )
    )

    print()
    print(
        f"Selected service: {service_name}"
    )
    print(
        f"Price: R{service_price:.2f}"
    )
    print(
        f"Deposit: R{deposit:.2f}"
    )

    event_response = get_event_type()

    event = get_event_from_response(
        event_response
    )

    if not event:
        print(
            "ERROR: Cal.com event could not be found."
        )
        return

    event_type_id = event.get("id")

    if not event_type_id:
        print(
            "ERROR: Cal.com Event Type ID not found."
        )
        return

    while True:

        booking_date = input(
            "\nEnter booking date (YYYY-MM-DD): "
        ).strip()

        if not booking_date:
            print(
                "ERROR: Booking date is required."
            )
            continue

        slots_data = get_available_slots(
            event_type_id,
            booking_date
        )

        if not slots_data:
            print(
                "ERROR: Could not retrieve availability."
            )

            retry = input(
                "Would you like to enter another "
                "date? (Y/N): "
            ).strip().lower()

            if retry == "y":
                continue

            print(
                "Booking process cancelled."
            )
            return

        available_data = slots_data.get(
            "data",
            {}
        )

        available_slots = available_data.get(
            booking_date,
            []
        )

        if not available_slots:
            print(
                f"No available booking times on "
                f"{booking_date}."
            )

            retry = input(
                "Would you like to choose another "
                "date? (Y/N): "
            ).strip().lower()

            if retry == "y":
                continue

            print(
                "Booking process cancelled."
            )
            return

        break

    print()
    print(
        f"Available booking times for "
        f"{booking_date}:"
    )

    for index, slot in enumerate(
        available_slots,
        start=1
    ):
        print(
            f"{index}. "
            f"{slot.get('start')} -> "
            f"{slot.get('end')}"
        )

    while True:

        try:
            slot_number = int(
                input(
                    "\nSelect a slot number: "
                ).strip()
            )

        except ValueError:
            print(
                "ERROR: Invalid slot selection."
            )
            continue

        if (
            slot_number < 1
            or slot_number > len(
                available_slots
            )
        ):
            print(
                "ERROR: Invalid slot selection."
            )
            continue

        break

    selected_slot = available_slots[
        slot_number - 1
    ]

    selected_start = selected_slot.get(
        "start"
    )

    selected_end = selected_slot.get(
        "end"
    )

    metadata = {
        "cust_id": str(cust_id),
        "serve_id": str(serve_id),
        "event_type_id": str(event_type_id),
        "firstname": firstname,
        "surname": surname,
        "cellphone": cellphone,
        "email": email,
        "booking_date": booking_date,
        "booking_start": selected_start,
        "booking_end": selected_end,
        "deposit": str(deposit),
        "paymentFacilitator": "yoco-online-checkout"
    }

    try:
        checkout = create_checkout(
            deposit,
            metadata=metadata
        )

    except Exception as error:
        print(
            "ERROR creating Yoco checkout:"
        )
        print(error)
        return

    checkout_id = checkout.get(
        "checkout_id"
    )

    checkout_url = checkout.get(
        "checkout_url"
    )

    if (
        not checkout_id
        or not checkout_url
    ):
        print(
            "ERROR: Yoco checkout information "
            "was not returned."
        )
        return

    print()
    print(
        f"Deposit required: R{deposit:.2f}"
    )
    print()
    print(
        "Yoco payment link:"
    )
    print(
        checkout_url
    )
    print()
    print(
        "Payment is required before the "
        "booking can be confirmed."
    )


if __name__ == "__main__":
    booking_workflow()