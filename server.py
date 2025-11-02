from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import uuid
import os

# -------------------------
# Flask App
# -------------------------
app = Flask(__name__)
CORS(app)

# -------------------------
# Resend API Config
# -------------------------
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RESEND_URL = "https://api.resend.com/emails"

# -------------------------
# Booking Route
# -------------------------
@app.route("/send-booking", methods=["POST"])
def send_booking():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    whatsapp = data.get("whatsapp")
    service = data.get("service")
    date = data.get("date")
    time = data.get("time")
    job = data.get("job", "Not specified")
    location = data.get("location", "")
    provider = data.get("provider", "Not assigned")

    appointment_id = str(uuid.uuid4()).split("-")[0].upper()

    subject_admin = f"New Booking: {service} by {name} (ID: {appointment_id})"
    subject_user = f"Your Appointment Confirmation (ID: {appointment_id})"

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color:#1E3A8A;">New Booking Received!</h2>
            <p><strong>Appointment ID:</strong> <span style="color:#DC2626;">{appointment_id}</span></p>
            <p><strong>Service Provider:</strong> {provider}</p>
            <p><strong>Customer Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Contact No.:</strong> {phone}</p>
            <p><strong>WhatsApp No.:</strong> {whatsapp}</p>
            <p><strong>Service:</strong> {service}</p>
            <p><strong>Job Description:</strong> {job}</p>
            <p><strong>Date & Time:</strong> {date} at {time}</p>
            <p><strong>Location:</strong> {location}</p>
            <hr/>
            <p style="color:gray;">You will be contacted shortly for service charges and payment proceeding...</p>
            <p style="color:gray;">This is an automated booking notification from <b>SevaSetu</b>.</p>
        </body>
    </html>
    """

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    payload_admin = {
        "from": "SevaSetu <noreply@sevasetu.in>",
        "to": ["sevasetu.services@gmail.com"],
        "subject": subject_admin,
        "html": html_content
    }

    payload_user = {
        "from": "SevaSetu <noreply@sevasetu.in>",
        "to": [email],
        "subject": subject_user,
        "html": html_content
    }

    try:
        res_admin = requests.post(RESEND_URL, headers=headers, json=payload_admin)
        res_user = requests.post(RESEND_URL, headers=headers, json=payload_user)

        if res_admin.status_code == 200 and res_user.status_code == 200:
            return jsonify({
                "success": True,
                "appointment_id": appointment_id,
                "message": f"✅ Booking Confirmed! Your Appointment ID is {appointment_id}"
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Error from Resend API: {res_admin.text or res_user.text}"
            })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# -------------------------
# Run Flask App
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
