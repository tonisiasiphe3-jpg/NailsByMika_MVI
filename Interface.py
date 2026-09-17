
import streamlit as st
import oracle_api
import calcom_api
import yoco

from datetime import datetime


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nails By Mika",
    page_icon="💅",
    layout="centered"
)


# ============================================================
# SESSION STATE
# ============================================================

if "selected_service" not in st.session_state:
    st.session_state["selected_service"] = None

if "customer_details" not in st.session_state:
    st.session_state["customer_details"] = None

if "available_slots" not in st.session_state:
    st.session_state["available_slots"] = None

if "selected_slot" not in st.session_state:
    st.session_state["selected_slot"] = None

if "selected_slot_display" not in st.session_state:
    st.session_state["selected_slot_display"] = None

if "booking_created" not in st.session_state:
    st.session_state["booking_created"] = False

if "booking_result" not in st.session_state:
    st.session_state["booking_result"] = None

if "payment_created" not in st.session_state:
    st.session_state["payment_created"] = False

if "payment_result" not in st.session_state:
    st.session_state["payment_result"] = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_field(data, *names):

    if not isinstance(data, dict):
        return None

    for name in names:

        if name in data:
            return data[name]

    return None


def extract_customer_id(data):

    if not data:
        return None

    customer_id = get_field(
        data,
        "CUST_ID",
        "cust_id"
    )

    if customer_id is not None:
        return customer_id

    nested_data = data.get("data")

    if isinstance(nested_data, dict):

        customer_id = get_field(
            nested_data,
            "CUST_ID",
            "cust_id"
        )

        if customer_id is not None:
            return customer_id

    return None


def extract_calcom_booking_id(data):

    if not isinstance(data, dict):
        return None

    possible_fields = [
        "id",
        "bookingId",
        "booking_id",
        "uid"
    ]

    for field in possible_fields:

        value = data.get(field)

        if value is not None:
            return value

    nested_data = data.get("data")

    if isinstance(nested_data, dict):

        for field in possible_fields:

            value = nested_data.get(field)

            if value is not None:
                return value

    nested_booking = data.get("booking")

    if isinstance(nested_booking, dict):

        for field in possible_fields:

            value = nested_booking.get(field)

            if value is not None:
                return value

    return None


def extract_oracle_booking_id(data):

    if not isinstance(data, dict):
        return None

    possible_fields = [
        "BOOKING_ID",
        "booking_id",
        "B_ID",
        "b_id"
    ]

    for field in possible_fields:

        value = data.get(field)

        if value is not None:
            return value

    nested_data = data.get("data")

    if isinstance(nested_data, dict):

        for field in possible_fields:

            value = nested_data.get(field)

            if value is not None:
                return value

    return None


def format_slot(slot_time):

    try:

        parsed_time = datetime.fromisoformat(
            slot_time.replace(
                "Z",
                "+00:00"
            )
        )

        return parsed_time.strftime(
            "%A, %d %B %Y at %H:%M"
        )

    except Exception:

        return slot_time


# ============================================================
# HEADER
# ============================================================

st.title("💅 Nails By Mika")

st.write(
    "Welcome to Nails By Mika. "
    "Book your nail appointment below."
)

st.divider()


# ============================================================
# 1. SERVICES
# ============================================================

st.header("1. Choose a Service")


try:

    services_data = oracle_api.get_services()

    services = services_data.get(
        "items",
        []
    )

except Exception as error:

    services = []

    st.error(
        f"Unable to load services from Oracle: {error}"
    )


service_options = {}


for service in services:

    serve_id = get_field(
        service,
        "serve_id",
        "SERVE_ID"
    )

    service_name = get_field(
        service,
        "service_name",
        "SERVICE_NAME"
    )

    price = get_field(
        service,
        "price",
        "PRICE"
    )

    deposit = get_field(
        service,
        "deposit",
        "DEPOSIT"
    )

    if serve_id is not None:

        service_name = str(
            service_name
        ).strip()

        display_name = (
            f"{service_name} — "
            f"R{float(price):.2f} "
            f"(Deposit: R{float(deposit):.2f})"
        )

        service_options[display_name] = {

            "serve_id":
                serve_id,

            "service_name":
                service_name,

            "price":
                price,

            "deposit":
                deposit
        }


selected_service_display = st.selectbox(

    "Select a service",

    options=[
        "Please select a service"
    ] + list(service_options.keys())
)


if selected_service_display != "Please select a service":

    selected_service = service_options[
        selected_service_display
    ]

    st.session_state[
        "selected_service"
    ] = selected_service

else:

    st.session_state[
        "selected_service"
    ] = None


st.divider()


# ============================================================
# 2. CUSTOMER DETAILS
# ============================================================

st.header("2. Customer Details")


firstname = st.text_input(
    "First Name",
    placeholder="Enter your first name",
    key="customer_firstname"
)


surname = st.text_input(
    "Surname",
    placeholder="Enter your surname",
    key="customer_surname"
)


cellphone = st.text_input(
    "Cellphone",
    placeholder="0821234567",
    key="customer_cellphone"
)


email = st.text_input(
    "Email",
    placeholder="example@email.com",
    key="customer_email"
)


# ============================================================
# 3. CHOOSE DATE
# ============================================================

st.header("3. Choose a Date")


booking_date = st.date_input(
    "Select your appointment date"
)


st.divider()


# ============================================================
# 4. CHECK CAL.COM AVAILABILITY
# ============================================================

st.header("4. Check Availability")


selected_service = st.session_state.get(
    "selected_service"
)


if selected_service is None:

    st.info(
        "Please select a service first."
    )

else:

    if st.button(
        "Check Available Times",
        use_container_width=True
    ):

        try:

            event_response = (
                calcom_api.get_event_type()
            )

            event = (
                calcom_api.get_event_from_response(
                    event_response
                )
            )

            if event is None:

                st.error(
                    "Unable to retrieve the Cal.com event."
                )

            else:

                event_type_id = event.get(
                    "id"
                )

                date_string = booking_date.strftime(
                    "%Y-%m-%d"
                )

                slots_data = (
                    calcom_api.get_available_slots(
                        event_type_id,
                        date_string
                    )
                )

                if not slots_data:

                    st.session_state[
                        "available_slots"
                    ] = None

                    st.session_state[
                        "selected_slot"
                    ] = None

                    st.session_state[
                        "selected_slot_display"
                    ] = None

                    st.error(
                        "Unable to retrieve availability "
                        "from Cal.com."
                    )

                else:

                    st.session_state[
                        "available_slots"
                    ] = slots_data

                    st.session_state[
                        "selected_slot"
                    ] = None

                    st.session_state[
                        "selected_slot_display"
                    ] = None

                    st.success(
                        "Availability loaded successfully."
                    )

        except Exception as error:

            st.error(
                f"Error checking availability: {error}"
            )


# ============================================================
# 5. DISPLAY AVAILABLE TIMES
# ============================================================

available_slots = st.session_state.get(
    "available_slots"
)


if available_slots:

    slot_data = available_slots.get(
        "data",
        {}
    )

    all_slots = []


    for date_value, slots in slot_data.items():

        for slot in slots:

            if isinstance(slot, dict):

                slot_time = (
                    slot.get("start")
                    or slot.get("time")
                )

            else:

                slot_time = slot

            if slot_time:

                all_slots.append(
                    slot_time
                )


    if all_slots:

        st.subheader(
            "Available Appointment Times"
        )

        slot_labels = []

        slot_lookup = {}


        for slot_time in all_slots:

            friendly_time = format_slot(
                slot_time
            )

            slot_labels.append(
                friendly_time
            )

            slot_lookup[
                friendly_time
            ] = slot_time


        previous_slot = (
            st.session_state.get(
                "selected_slot_display"
            )
        )


        default_index = 0


        if previous_slot in slot_labels:

            default_index = slot_labels.index(
                previous_slot
            )


        selected_display_time = st.radio(

            "Choose an available time",

            options=slot_labels,

            index=default_index
        )


        selected_raw_slot = slot_lookup[
            selected_display_time
        ]


        st.session_state[
            "selected_slot"
        ] = selected_raw_slot


        st.session_state[
            "selected_slot_display"
        ] = selected_display_time


        st.success(
            f"Selected: {selected_display_time}"
        )


    else:

        st.warning(
            "No available appointment times "
            "were found for this date."
        )


elif available_slots is not None:

    st.warning(
        "No available appointment times "
        "were found for this date."
    )


st.divider()


# ============================================================
# 6. BOOKING SUMMARY
# ============================================================

st.header("6. Booking Summary")


selected_service = st.session_state.get(
    "selected_service"
)


customer_details = st.session_state.get(
    "customer_details"
)


selected_slot = st.session_state.get(
    "selected_slot"
)


selected_slot_display = st.session_state.get(
    "selected_slot_display"
)


if selected_service:

    st.write(
        f"**Service:** "
        f"{selected_service['service_name']}"
    )

    st.write(
        f"**Price:** "
        f"R{float(selected_service['price']):.2f}"
    )

    st.write(
        f"**Deposit:** "
        f"R{float(selected_service['deposit']):.2f}"
    )


if customer_details:

    st.write(
        f"**Customer:** "
        f"{customer_details['firstname']} "
        f"{customer_details['surname']}"
    )

    st.write(
        f"**Cellphone:** "
        f"{customer_details['cellphone']}"
    )

    st.write(
        f"**Email:** "
        f"{customer_details['email']}"
    )


if selected_slot_display:

    st.write(
        f"**Appointment:** "
        f"{selected_slot_display}"
    )


st.divider()


# ============================================================
# 7. CREATE BOOKING
# ============================================================

st.header("7. Create Booking")


firstname = st.session_state.get(
    "customer_firstname"
)

surname = st.session_state.get(
    "customer_surname"
)

cellphone = st.session_state.get(
    "customer_cellphone"
)

email = st.session_state.get(
    "customer_email"
)


firstname = (
    ""
    if firstname is None
    else str(firstname)
)


surname = (
    ""
    if surname is None
    else str(surname)
)


cellphone = (
    ""
    if cellphone is None
    else str(cellphone)
)


email = (
    ""
    if email is None
    else str(email)
)


selected_service = st.session_state.get(
    "selected_service"
)


selected_slot = st.session_state.get(
    "selected_slot"
)


selected_slot_display = st.session_state.get(
    "selected_slot_display"
)


customer_complete = (

    firstname.strip() != ""

    and

    surname.strip() != ""

    and

    cellphone.strip() != ""

    and

    email.strip() != ""
)


service_selected = (
    selected_service is not None
)


time_selected = (
    selected_slot is not None
)


if not customer_complete:

    st.warning(
        "Please complete all customer details."
    )


if not service_selected:

    st.warning(
        "Please select a service."
    )


if not time_selected:

    st.warning(
        "Please select an available appointment time."
    )


if (
    customer_complete
    and
    service_selected
    and
    time_selected
):

    if not st.session_state.get(
        "booking_created",
        False
    ):

        st.success(
            "All booking details are complete."
        )


        if st.button(
            "Create Booking",
            type="primary",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Creating your booking..."
                ):

                    # ====================================================
                    # 1. CREATE CUSTOMER IN ORACLE
                    # ====================================================

                    st.info(
                        "Saving customer details..."
                    )


                    customer_response = (
                        oracle_api.create_customer(
                            firstname,
                            surname,
                            cellphone,
                            email
                        )
                    )


                    customer_id = (
                        extract_customer_id(
                            customer_response
                        )
                    )


                    if not customer_id:

                        st.error(
                            "Customer was not created successfully in Oracle."
                        )

                        st.write(
                            "Oracle customer response:"
                        )

                        st.write(
                            customer_response
                        )

                        st.stop()


                    # ====================================================
                    # 2. GET CAL.COM EVENT
                    # ====================================================

                    event_response = (
                        calcom_api.get_event_type()
                    )


                    if not event_response:

                        st.error(
                            "Could not retrieve the Cal.com event."
                        )

                        st.stop()


                    event_type = (
                        calcom_api.get_event_from_response(
                            event_response
                        )
                    )


                    if not event_type:

                        st.error(
                            "Could not find the Cal.com event."
                        )

                        st.stop()


                    event_type_id = event_type.get(
                        "id"
                    )


                    # ====================================================
                    # 3. CREATE BOOKING IN CAL.COM
                    # ====================================================

                    st.info(
                        "Creating your appointment in Cal.com..."
                    )


                    calcom_result = (
                        calcom_api.create_booking(
                            event_type_id,
                            selected_slot,
                            firstname,
                            surname,
                            cellphone,
                            email
                        )
                    )


                    # ====================================================
                    # 4. CHECK CAL.COM RESULT
                    # ====================================================

                    if not calcom_result:

                        st.error(
                            "Cal.com did not return a response."
                        )

                        st.stop()


                    if not calcom_result.get(
                        "success"
                    ):

                        st.error(
                            "Cal.com booking failed."
                        )

                        st.write(
                            "Cal.com response:"
                        )

                        st.write(
                            calcom_result
                        )

                        st.stop()


                    # ====================================================
                    # 5. GET CAL.COM BOOKING ID
                    # ====================================================

                    calcom_booking_id = (
                        extract_calcom_booking_id(
                            calcom_result
                        )
                    )


                    if not calcom_booking_id:

                        st.error(
                            "Cal.com booking was created, "
                            "but the booking ID could not be found."
                        )

                        st.write(
                            calcom_result
                        )

                        st.stop()


                    # ====================================================
                    # 6. CREATE BOOKING IN ORACLE
                    # ====================================================

                    st.info(
                        "Saving booking to Oracle..."
                    )


                    oracle_booking = (
                        oracle_api.create_booking(
                            customer_id,
                            selected_service["serve_id"],
                            selected_slot,
                            "Pending",
                            calcom_booking_id
                        )
                    )


                    # ====================================================
                    # 7. GET ORACLE BOOKING ID
                    # ====================================================

                    oracle_booking_id = (
                        extract_oracle_booking_id(
                            oracle_booking
                        )
                    )


                    # ====================================================
                    # 8. SAVE BOOKING RESULT
                    # ====================================================

                    st.session_state[
                        "booking_created"
                    ] = True


                    st.session_state[
                        "booking_result"
                    ] = {

                        "customer_id":
                            customer_id,

                        "oracle_booking_id":
                            oracle_booking_id,

                        "calcom_booking_id":
                            calcom_booking_id,

                        "oracle_booking":
                            oracle_booking,

                        "service":
                            selected_service,

                        "customer":
                            {

                                "firstname":
                                    firstname,

                                "surname":
                                    surname,

                                "cellphone":
                                    cellphone,

                                "email":
                                    email
                            },

                        "slot":
                            selected_slot,

                        "appointment":
                            selected_slot_display,

                        "price":
                            selected_service["price"],

                        "deposit":
                            selected_service["deposit"]
                    }


                    st.rerun()


            except Exception as error:

                st.error(
                    "Something went wrong while creating the booking."
                )

                st.exception(
                    error
                )


    else:

        st.success(
            "Your booking has already been created."
        )


# ============================================================
# 8. BOOKING CONFIRMATION
# ============================================================

if st.session_state.get(
    "booking_created",
    False
):

    result = st.session_state.get(
        "booking_result"
    )


    if result:

        st.divider()


        st.header(
            "🎉 Booking Created"
        )


        st.success(
            "Your appointment has been successfully created."
        )


        st.write(
            f"**Customer:** "
            f"{result['customer']['firstname']} "
            f"{result['customer']['surname']}"
        )


        st.write(
            f"**Service:** "
            f"{result['service']['service_name']}"
        )


        st.write(
            f"**Appointment:** "
            f"{result['appointment']}"
        )


        st.write(
            f"**Price:** "
            f"R{float(result['price']):.2f}"
        )


        st.write(
            f"**Deposit:** "
            f"R{float(result['deposit']):.2f}"
        )


        st.write(
            f"**Cal.com Booking ID:** "
            f"{result['calcom_booking_id']}"
        )


        if result.get(
            "oracle_booking_id"
        ):

            st.write(
                f"**Oracle Booking ID:** "
                f"{result['oracle_booking_id']}"
            )


        st.info(
            "Your appointment is currently pending payment. "
            "Please pay the deposit below to confirm your booking."
        )


# ============================================================
# 9. PAY DEPOSIT
# ============================================================

if st.session_state.get(
    "booking_created",
    False
):

    result = st.session_state.get(
        "booking_result"
    )


    if result:

        st.divider()


        st.header(
            "💳 9. Pay Deposit"
        )


        deposit_amount = float(
            result["deposit"]
        )


        total_price = float(
            result["price"]
        )


        st.write(
            f"**Service:** "
            f"{result['service']['service_name']}"
        )


        st.write(
            f"**Total Price:** "
            f"R{total_price:.2f}"
        )


        st.write(
            f"**Deposit Required:** "
            f"R{deposit_amount:.2f}"
        )


        st.info(
            "A 50% deposit is required to confirm "
            "your appointment."
        )


        # ====================================================
        # CREATE YOCO CHECKOUT
        # ====================================================

        if not st.session_state.get(
            "payment_created",
            False
        ):


            if st.button(
                f"💳 Pay R{deposit_amount:.2f} Deposit",
                type="primary",
                use_container_width=True
            ):


                try:

                    with st.spinner(
                        "Preparing secure payment..."
                    ):


                        metadata = {

                            "calcom_booking_id":
                                str(
                                    result[
                                        "calcom_booking_id"
                                    ]
                                ),

                            "customer_email":
                                str(
                                    result[
                                        "customer"
                                    ][
                                        "email"
                                    ]
                                )
                        }


                        if result.get(
                            "oracle_booking_id"
                        ):

                            metadata[
                                "oracle_booking_id"
                            ] = str(
                                result[
                                    "oracle_booking_id"
                                ]
                            )


                        checkout_result = (
                            yoco.create_checkout(
                                amount=deposit_amount,
                                currency="ZAR",
                                metadata=metadata
                            )
                        )


                        checkout_url = (
                            checkout_result.get(
                                "checkout_url"
                            )
                        )


                        checkout_id = (
                            checkout_result.get(
                                "checkout_id"
                            )
                        )


                        if not checkout_url:

                            st.error(
                                "Yoco did not return a payment link."
                            )


                            st.write(
                                "Yoco response:"
                            )


                            st.write(
                                checkout_result
                            )


                            st.stop()


                        st.session_state[
                            "payment_created"
                        ] = True


                        st.session_state[
                            "payment_result"
                        ] = {

                            "checkout_id":
                                checkout_id,

                            "checkout_url":
                                checkout_url,

                            "amount":
                                deposit_amount
                        }


                        st.rerun()


                except Exception as error:

                    st.error(
                        "Unable to create the Yoco payment."
                    )


                    st.exception(
                        error
                    )


        # ====================================================
        # DISPLAY YOCO PAYMENT BUTTON
        # ====================================================

        if st.session_state.get(
            "payment_created",
            False
        ):


            payment_result = (
                st.session_state.get(
                    "payment_result"
                )
            )


            if payment_result:

                st.success(
                    "Your secure payment checkout is ready."
                )


                st.write(
                    f"**Amount to Pay:** "
                    f"R{float(payment_result['amount']):.2f}"
                )


                st.link_button(
                    "💳 Continue to Yoco Payment",
                    payment_result[
                        "checkout_url"
                    ],
                    use_container_width=True
                )


                st.caption(
                    "Click the button above to open the "
                    "secure Yoco payment page."
                )


# ============================================================
# 10. START NEW BOOKING
# ============================================================

if st.session_state.get(
    "booking_created",
    False
):

    st.divider()


    if st.button(
        "Start New Booking",
        use_container_width=True
    ):


        keys_to_clear = [

            "selected_service",

            "customer_details",

            "customer_firstname",

            "customer_surname",

            "customer_cellphone",

            "customer_email",

            "available_slots",

            "selected_slot",

            "selected_slot_display",

            "booking_created",

            "booking_result",

            "payment_created",

            "payment_result"
        ]


        for key in keys_to_clear:

            if key in st.session_state:

                del st.session_state[key]


        st.rerun()


# ============================================================
# MANAGE BOOKING
# ============================================================

st.header("Manage Booking")

st.write("Need to cancel or reschedule an appointment?")

st.info(
    "Enter your Cal.com booking ID below to manage your appointment."
)

manage_booking_id = st.text_input(
    "Cal.com Booking ID",
    placeholder="Enter your booking ID"
)

manage_action = st.selectbox(
    "What would you like to do?",
    [
        "Select an option",
        "Cancel Booking",
        "Reschedule Booking"
    ]
)

if manage_action == "Cancel Booking":

    if st.button("Cancel Appointment"):

        if not manage_booking_id.strip():

            st.error("Please enter your Cal.com booking ID.")

        else:

            try:

                booking_id = int(
                    manage_booking_id.strip()
                )

                result = calcom_api.cancel_booking(
                    booking_id
                )

                st.success(
                    "Your appointment has been cancelled successfully."
                )

                st.write(result)

            except Exception as e:

                st.error(
                    "Unable to cancel the appointment."
                )

                st.error(str(e))


elif manage_action == "Reschedule Booking":

    st.info(
        "To reschedule your appointment, Cal.com will provide the available booking options."
    )

    if st.button("Find Rescheduling Options"):

        if not manage_booking_id.strip():

            st.error(
                "Please enter your Cal.com booking ID."
            )

        else:

            try:

                booking_id = int(
                    manage_booking_id.strip()
                )

                reschedule_url = (
                    f"https://cal.com/nails-by-mika/reschedule/{booking_id}"
                )

                st.markdown(
                    f"[Open Cal.com Rescheduling]({reschedule_url})"
                )

            except Exception as e:

                st.error(
                    "Invalid booking ID."
                )

                st.error(str(e))