from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
import os
from openpyxl import Workbook, load_workbook

# -------------------------
# 1️⃣ Create Flask app
# -------------------------
app = Flask(__name__)
CORS(app)

# -------------------------
# 2️⃣ Route for booking
# -------------------------
@app.route("/send-booking", methods=["POST"])
def send_booking():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    service = data.get("service")
    date = data.get("date")
    time = data.get("time")
    job = data.get("job", "Not specified")
    location = data.get("location", "")
    provider = data.get("provider", "Not assigned")

    # Generate a unique appointment ID
    appointment_id = str(uuid.uuid4()).split("-")[0].upper()

    # Email setup (from ENV for security)
    sender_email = os.getenv("SENDER_EMAIL", "arnavp128@gmail.com")
    sender_password = os.getenv("SENDER_PASSWORD", "cyhy ppki rdny rjwc")
    admin_email = os.getenv("ADMIN_EMAIL", "arnavpundir22@gmail.com")

    body = f"""
    <html>
        <body>
            <h2 style="color:#1E3A8A;">New Booking Received!</h2>
            <p><strong>Appointment ID:</strong> <span style="color:#DC2626;">{appointment_id}</span></p>
            <p><strong>Service Provider:</strong> {provider}</p>
            <p><strong>Customer Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone}</p>
            <p><strong>Service:</strong> {service}</p>
            <p><strong>Job Description:</strong> {job}</p>
            <p><strong>Date & Time:</strong> {date} at {time}</p>
            <p><strong>Location:</strong> <span style="color:#1E40AF;">{location}</span></p>
            <hr/>
            <p style="color:gray;">You will be contacted shortly for service charges and payment proceeding...</p>
            <p style="color:gray;">This is an automated booking notification.</p>
        </body>
    </html>
    """

    try:
        # --- Send to admin ---
        msg_admin = MIMEMultipart()
        msg_admin["Subject"] = f"New Booking: {service} by {name} (ID: {appointment_id})"
        msg_admin["From"] = sender_email
        msg_admin["To"] = admin_email
        msg_admin.attach(MIMEText(body, "html"))

        # --- Send copy to user ---
        msg_user = MIMEMultipart()
        msg_user["Subject"] = f"Your Appointment Confirmation (ID: {appointment_id})"
        msg_user["From"] = sender_email
        msg_user["To"] = email
        msg_user.attach(MIMEText(body, "html"))

        # --- Send emails ---
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, admin_email, msg_admin.as_string())
            server.sendmail(sender_email, email, msg_user.as_string())

        # Save to Excel
        excel_file = "bookings.xlsx"
        if os.path.exists(excel_file):
            wb = load_workbook(excel_file)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(["Appointment ID", "Provider", "Customer Name", "Email", "Phone", "Service", "Job", "Date", "Time", "Location"])

        ws.append([appointment_id, provider, name, email, phone, service, job, date, time, location])
        wb.save(excel_file)

        return jsonify({
            "success": True,
            "appointment_id": appointment_id,
            "message": f"✅ Booking Confirmed! Your Appointment ID is {appointment_id}"
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# -------------------------
# 3️⃣ Route for Contact Us
# -------------------------
@app.route("/contact-us", methods=["POST"])
def contact_us():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    subject = data.get("subject", "No Subject")
    message = data.get("message", "")

    # Generate a unique token number
    token_no = "CONTACT-" + str(uuid.uuid4()).split("-")[0].upper()

    # Email setup
    sender_email = os.getenv("SENDER_EMAIL", "arnavp128@gmail.com")
    sender_password = os.getenv("SENDER_PASSWORD", "your-app-password")
    admin_email = os.getenv("ADMIN_EMAIL", "arnavpundir22@gmail.com")

    body = f"""
    <html>
        <body>
            <h2 style="color:#047857;">New Contact Request!</h2>
            <p><strong>Token No:</strong> <span style="color:#DC2626;">{token_no}</span></p>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Message:</strong><br/>{message}</p>
            <hr/>
            <p style="color:gray;">This is an automated contact notification.</p>
        </body>
    </html>
    """

    try:
        # --- Send to admin ---
        msg_admin = MIMEMultipart()
        msg_admin["Subject"] = f"Contact Request from {name} (Token: {token_no})"
        msg_admin["From"] = sender_email
        msg_admin["To"] = admin_email
        msg_admin.attach(MIMEText(body, "html"))

        # --- Send copy to user ---
        msg_user = MIMEMultipart()
        msg_user["Subject"] = f"Your Contact Request (Token: {token_no})"
        msg_user["From"] = sender_email
        msg_user["To"] = email
        msg_user.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, admin_email, msg_admin.as_string())
            server.sendmail(sender_email, email, msg_user.as_string())

        # Save to Excel
        excel_file = "contacts.xlsx"
        if os.path.exists(excel_file):
            wb = load_workbook(excel_file)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(["Token No", "Name", "Email", "Subject", "Message"])

        ws.append([token_no, name, email, subject, message])
        wb.save(excel_file)

        return jsonify({
            "success": True,
            "token_no": token_no,
            "message": f"📩 Contact request submitted! Your Token No is {token_no}"
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# -------------------------
# Run the Flask app
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


