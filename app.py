import sys
import webbrowser
import geocoder
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from flask import Flask, request, jsonify
import smtplib
from twilio.rest import Client
from flask_cors import CORS
import threading

# Flask Backend for Alerts
app = Flask(_name_)
CORS(app)  # Enable CORS for frontend-backend communication

# Replace with actual credentials
EMERGENCY_CONTACTS = ["+11234567890", "emergency@gmail.com"]

TWILIO_SID = "AC56ac6eb3ae2c0f4ee04cc385cc9b9b63"
TWILIO_AUTH_TOKEN = "a1c96f3fd60cda807a5deb56ef00b7d3"
TWILIO_PHONE = "+12233380889"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASS = "your-password" 


# Function to send SMS
def send_sms(message):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        for contact in EMERGENCY_CONTACTS:
            if contact.startswith("+"):  # Send SMS only to phone numbers
                msg = client.messages.create(body=message, from_=TWILIO_PHONE, to=contact)
                print(f"SMS Sent to {contact}: SID {msg.sid}")  # Debugging
        return "SMS Sent"
    except Exception as e:
        print(f"SMS Error: {str(e)}")  # Print error for debugging
        return f"SMS Error: {str(e)}"

# Function to send Email
def send_email(subject, message):
    try:
        print(f"Connecting to SMTP server {EMAIL_HOST}:{EMAIL_PORT}...")  # Debugging
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        print("Logging in to email...")  # Debugging
        server.login(EMAIL_USER, EMAIL_PASS)
        
        for contact in EMERGENCY_CONTACTS:
            if "@" in contact:
                server.sendmail(EMAIL_USER, contact, f"Subject: {subject}\n\n{message}")
                print(f"Email sent to {contact}")  # Debugging
                
        server.quit()
        return "Email Sent"
    except Exception as e:
        print(f"Email Error: {str(e)}")  # Print error for debugging
        return f"Email Error: {str(e)}"


# API to receive emergency alerts
@app.route("/alert", methods=["POST"])
def receive_alert():
    data = request.json
    location = data.get("location", "Unknown location")

    message = f"🚨 EMERGENCY ALERT 🚨\nLocation: {location}\nHelp Needed Immediately!"

    sms_status = send_sms(message)
    email_status = send_email("Emergency Alert", message)

    return jsonify({"status": "Alert Received", "sms": sms_status, "email": email_status})

# Start Flask server in a separate thread
def run_flask():
    app.run(debug=True, use_reloader=False)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# PyQt6 GUI for the Safety App
class SafetyApp(QWidget):
    def _init_(self):
        super()._init_()

        self.setWindowTitle("Women's Safety App")
        self.setFixedSize(400, 350)
        
        # Set background color
        self.setStyleSheet("background-color: #F9E9E3;")

        # Label
        self.label = QLabel("Stay Safe! Press the buttons in case of emergency.", self)
        self.label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.label.setStyleSheet("color: #333; padding: 10px;")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Emergency Alert Button
        self.emergency_button = QPushButton("🚨 Alert Now")
        self.emergency_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.emergency_button.setStyleSheet("background-color: #D72638; color: white; border-radius: 15px; padding: 10px;")
        self.emergency_button.clicked.connect(self.trigger_alert)

        # Location Sharing Button
        self.location_button = QPushButton("📍 Share Location")
        self.location_button.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.location_button.setStyleSheet("background-color: #007BFF; color: white; border-radius: 15px; padding: 10px;")
        self.location_button.clicked.connect(self.send_location)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.emergency_button)
        layout.addWidget(self.location_button)
        self.setLayout(layout)

    def trigger_alert(self):
        # Get current location
        g = geocoder.ip("me")
        if g.ok:
            latitude, longitude = g.latlng
            location = f"{latitude}, {longitude}"
        else:
            location = "Unknown location"

        # Send alert to Flask backend
        url = "http://127.0.0.1:5000/alert"
        data = {"location": location}
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                self.label.setText("🚨 Alert Sent! Help is on the way.")
            else:
                self.label.setText("⚠️ Failed to send alert.")
        except requests.exceptions.ConnectionError:
            self.label.setText("⚠️ Backend not running.")

    def send_location(self):
        # Get current location
        g = geocoder.ip("me")
        if g.ok:
            latitude, longitude = g.latlng
            maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"

            # Open Google Maps
            webbrowser.open(maps_url)

            # Update label
            self.label.setText(f"📍 Location sent! Open [Google Maps]({maps_url}) to view.")
        else:
            self.label.setText("⚠️ Location not found.")

# Run PyQt6 application
if _name_ == "_main_":
    app = QApplication(sys.argv)
    window = SafetyApp()
    window.show()
    sys.exit(app.exec())