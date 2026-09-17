

from flask import Flask, request, jsonify
import oracle_api
import calcom_api

app = Flask(__name__)
print("ORACLE API FILE:", oracle_api.__file__)

@app.route("/payment-success", methods=["POST"])
def payment_success():

    data = request.get_json()

    print()
    print("==============================================")
    print("       PAYMENT WEBHOOK RECEIVED")
    print("==============================================")

    if not data:
        print("No JSON data received")
        return jsonify({
            "success": False,
            "message": "No JSON data received"
        }), 400

    event_type = data.get("type")

    print("Yoco event type:", event_type)

    if event_type != "payment.succeeded":
        print("Event ignored")

        return jsonify({
            "success": True,
            "message": "Event ignored"
        }), 200

    payload = data.get("payload", {})

    yoco_payment_id = data.get("id")

    if not yoco_payment_id:
        yoco_payment_id = payload.get("id")

    amount_cents = payload.get("amount")
    currency = payload.get("currency")
    payment_status = payload.get("status")

    metadata = payload.get("metadata", {})

    oracle_booking_id = metadata.get("oracle_booking_id")
    calcom_booking_id = metadata.get("calcom_booking_id")
    customer_email = metadata.get("customer_email")

    print("Payment ID:", yoco_payment_id)
    print("Amount:", amount_cents)
    print("Currency:", currency)
    print("Payment status:", payment_status)

    print("Metadata:")
    print(metadata)

    if not yoco_payment_id:

        print("No Yoco payment ID found")

        return jsonify({
            "success": False,
            "message": "Missing Yoco payment ID"
        }), 400

    if amount_cents is None:

        print("No payment amount found")

        return jsonify({
            "success": False,
            "message": "Missing payment amount"
        }), 400

    print()
    print("Checking whether this Yoco payment was already processed...")

    payments_data = oracle_api.get_payments()

    existing_payment = None

    if payments_data:

        payment_items = payments_data.get(
            "items",
            []
        )

        for payment in payment_items:

            existing_yoco_id = payment.get(
                "yoco_payment_id"
            )

            if existing_yoco_id:

                if str(existing_yoco_id) == str(
                    yoco_payment_id
                ):

                    existing_payment = payment

                    break

    if existing_payment:

        print()
        print("==============================================")
        print("       DUPLICATE PAYMENT DETECTED")
        print("==============================================")

        print(
            "Yoco Payment ID:",
            yoco_payment_id
        )

        print(
            "Existing Oracle Payment ID:",
            existing_payment.get("pay_id")
        )

        print("No new payment will be created.")

        print()

        return jsonify({
            "success": True,
            "message": "Payment already processed",
            "payment_id": yoco_payment_id,
            "oracle_payment_id": existing_payment.get(
                "pay_id"
            )
        }), 200

    bookings_data = oracle_api.get_bookings()

    booking = None

    if bookings_data:

        booking_items = bookings_data.get(
            "items",
            []
        )

        if oracle_booking_id:

            print()
            print(
                "Searching Oracle using Oracle booking ID..."
            )

            for item in booking_items:

                if str(
                    item.get("booking_id")
                ) == str(
                    oracle_booking_id
                ):

                    booking = item

                    break

        if booking is None and calcom_booking_id:

            print()
            print(
                "Searching Oracle using Cal.com booking ID..."
            )

            for item in booking_items:

                oracle_calcom_id = item.get(
                    "calcom_booking_id"
                )

                if oracle_calcom_id:

                    if str(
                        oracle_calcom_id
                    ) == str(
                        calcom_booking_id
                    ):

                        booking = item

                        break

        if (
            booking is None
            and not calcom_booking_id
            and customer_email
        ):

            print()
            print(
                "No Cal.com booking ID supplied."
            )

            print(
                "Searching Oracle using customer email..."
            )

            customers_data = oracle_api.get_customers()

            if customers_data:

                customer_items = customers_data.get(
                    "items",
                    []
                )

                matching_customer_id = None

                for customer in customer_items:

                    customer_email_value = customer.get(
                        "email"
                    )

                    if customer_email_value:

                        if (
                            str(
                                customer_email_value
                            ).strip().lower()
                            ==
                            str(
                                customer_email
                            ).strip().lower()
                        ):

                            matching_customer_id = customer.get(
                                "cust_id"
                            )

                            break

                if matching_customer_id:

                    for item in booking_items:

                        if str(
                            item.get("cust_id")
                        ) == str(
                            matching_customer_id
                        ):

                            if (
                                str(
                                    item.get(
                                        "status",
                                        ""
                                    )
                                ).lower()
                                == "pending"
                            ):

                                booking = item

                                break

    if booking is None:

        print()
        print("==============================================")
        print("          ORACLE BOOKING NOT FOUND")
        print("==============================================")

        print(
            "Oracle booking ID:",
            oracle_booking_id
        )

        print(
            "Cal.com booking ID:",
            calcom_booking_id
        )

        print(
            "Customer email:",
            customer_email
        )

        return jsonify({
            "success": False,
            "message": "Oracle booking not found"
        }), 404

    booking_id = booking.get(
        "booking_id"
    )

    cust_id = booking.get(
        "cust_id"
    )

    serve_id = booking.get(
        "serve_id"
    )

    booking_date = booking.get(
        "booking_date"
    )

    current_status = booking.get(
        "status"
    )

    existing_calcom_id = booking.get(
        "calcom_booking_id"
    )

    print()
    print("==============================================")
    print("           EXISTING ORACLE BOOKING")
    print("==============================================")

    print(
        "Oracle booking ID:",
        booking_id
    )

    print(
        "Customer ID:",
        cust_id
    )

    print(
        "Service ID:",
        serve_id
    )

    print(
        "Booking date:",
        booking_date
    )

    print(
        "Current status:",
        current_status
    )

    print(
        "Cal.com booking ID:",
        existing_calcom_id
    )

    amount = float(
        amount_cents
    ) / 100

    print(
        "Payment amount: R{:.2f}".format(
            amount
        )
    )

    print()
    update_result = oracle_api.update_booking(
    booking_id=booking_id,
    cust_id=cust_id,
    serve_id=serve_id,
    booking_date=booking_date,
    status="Confirmed",
    calcom_booking_id=(
        calcom_booking_id
        if calcom_booking_id
        else existing_calcom_id
    )
)

    print()
    print("ORACLE BOOKING UPDATE RESULT:")
    print(update_result)
    print()

    print()
    print("Creating Oracle payment...")

    payment_result = oracle_api.create_payment(
        booking_id=booking_id,
        amount=amount,
        status="Confirmed",
        yoco_payment_id=yoco_payment_id
    )

    print(
        "Oracle payment response:",
        payment_result
    )

    print()
    print("==============================================")
    print("        PAYMENT PROCESS COMPLETED")
    print("==============================================")

    return jsonify({
        "success": True,
        "message": "Payment processed successfully",
        "yoco_payment_id": yoco_payment_id,
        "oracle_booking_id": booking_id,
        "oracle_payment": payment_result
    }), 200


@app.route("/calcom-webhook", methods=["POST"])
def calcom_webhook():

    data = request.get_json()

    print()
    print("==============================================")
    print("          CAL.COM WEBHOOK RECEIVED")
    print("==============================================")

    print("Webhook data:")
    print(data)

    if not data:

        print("No JSON data received")

        return jsonify({
            "success": False,
            "message": "No JSON data received"
        }), 400

    event_type = data.get(
        "triggerEvent"
    )

    if not event_type:

        event_type = data.get(
            "event"
        )

    print(
        "Cal.com event:",
        event_type
    )

    payload = data.get(
        "payload",
        {}
    )

    booking_id = (
        payload.get("bookingId")
        or payload.get("id")
    )

    if not booking_id:

        booking_data = payload.get(
            "booking",
            {}
        )

        if isinstance(
            booking_data,
            dict
        ):

            booking_id = (
                booking_data.get("id")
                or booking_data.get("bookingId")
            )

    print(
        "Cal.com booking ID:",
        booking_id
    )

    if event_type == "BOOKING_CANCELLED":

        print()
        print(
            "Cal.com booking cancellation received."
        )

        bookings_data = oracle_api.get_bookings()

        booking = None

        if bookings_data:

            for item in bookings_data.get(
                "items",
                []
            ):

                oracle_calcom_id = item.get(
                    "calcom_booking_id"
                )

                if (
                    oracle_calcom_id
                    and booking_id
                    and str(
                        oracle_calcom_id
                    )
                    == str(
                        booking_id
                    )
                ):

                    booking = item

                    break

        if booking:

            print(
                "Oracle booking found:",
                booking.get("booking_id")
            )

            oracle_api.update_booking(
                booking_id=booking.get(
                    "booking_id"
                ),
                cust_id=booking.get(
                    "cust_id"
                ),
                serve_id=booking.get(
                    "serve_id"
                ),
                booking_date=booking.get(
                    "booking_date"
                ),
                status="Cancelled",
                calcom_booking_id=booking.get(
                    "calcom_booking_id"
                )
            )

            print(
                "Oracle booking marked as Cancelled."
            )

        else:

            print(
                "No matching Oracle booking found."
            )

        return jsonify({
            "success": True,
            "message": "Cancellation webhook processed"
        }), 200

    if event_type == "BOOKING_RESCHEDULED":

        print()
        print(
            "Cal.com booking reschedule received."
        )

        print(
            "Rescheduled booking:",
            booking_id
        )

        print(
            "Reschedule event acknowledged."
        )

        return jsonify({
            "success": True,
            "message": "Reschedule webhook received"
        }), 200

    print()
    print(
        "Cal.com event not specifically handled."
    )

    return jsonify({
        "success": True,
        "message": "Cal.com event received"
    }), 200


if __name__ == "__main__":

    print()
    print("==============================================")
    print("          NAILS BY MIKA WEBHOOK SERVER")
    print("==============================================")

    print("Payment webhook:")
    print("/payment-success")

    print()
    print("Cal.com webhook:")
    print("/calcom-webhook")

    print()
    print("Server running on port 5000")

    print("==============================================")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )