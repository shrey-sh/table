from pymongo import MongoClient

def create_collections():
    """
    Creates the collections and schema for the application in MongoDB Atlas.
    """
    # Connect to MongoDB Atlas
    CONNECTION_STRING = "mongodb+srv://shreyashestabit:Nuvac#3462@cluster0.m8wzm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your MongoDB Atlas URI
    # client = MongoClient(CONNECTION_STRING)
    
    client = MongoClient(CONNECTION_STRING, tls=True, tlsAllowInvalidCertificates=True)

    # Specify the database
    db = client["car_booking_system"]

    # Corporate Clients Collection
    corporate_clients_collection = db["corporate_clients"]
    corporate_clients_collection.insert_one({
        "corporate_id": None,  # Auto-generated unique identifier
        "company_name": "",  # Name of the corporate company
        "email": "",         # Email ID of the corporate client (unique)
        "phone": "",         # Contact number of the corporate client
        "password_hash": "", # Hashed password for authentication
        "created_at": ""     # Account creation timestamp
    })
    corporate_clients_collection.create_index("email", unique=True)

    # Users Collection
    users_collection = db["users"]
    users_collection.insert_one({
        "user_id": None,       # Auto-generated unique identifier
        "name": "",          # Name of the user
        "email": "",         # Email ID for the user (unique)
        "phone": "",         # Contact number of the user
        "password_hash": "", # Hashed password for authentication
        "user_type": "individual",  # Type of user (individual or corporate)
        "corporate_id": None,  # Associated corporate client (if applicable)
        "created_at": ""      # Account creation timestamp
    })
    users_collection.create_index("email", unique=True)

    # Cars Collection
    cars_collection = db["cars"]
    cars_collection.insert_one({
        "car_id": None,       # Auto-generated unique identifier
        "model": "",        # Car model name
        "type": "",         # Car type (e.g., Sedan, SUV)
        "license_plate": "", # License plate number (unique)
        "capacity": 0,        # Seating capacity
        "rate_per_km": 0.0    # Rate per kilometer
    })
    cars_collection.create_index("license_plate", unique=True)

    # Drivers Collection
    drivers_collection = db["drivers"]
    drivers_collection.insert_one({
        "driver_id": None,   # Auto-generated unique identifier
        "name": "",        # Full name of the driver
        "driver_license": "",  # License number (unique)
        "phone": "",       # Contact number
        "experience": 0,    # Years of driving experience
        "assigned_car_id": None  # Car ID assigned to the driver
    })
    drivers_collection.create_index("driver_license", unique=True)

    # Bookings Collection
    bookings_collection = db["bookings"]
    bookings_collection.insert_one({
        "booking_id": None,     # Auto-generated unique identifier
        "user_id": None,        # Reference to Users collection
        "car_id": None,         # Reference to Cars collection
        "driver_id": None,      # Reference to Drivers collection
        "booking_date": "",   # Date of the booking
        "start_time": "",     # Start time of the booking
        "end_time": "",       # End time of the booking
        "total_price": 0.0,    # Total price for the booking
        "payment_status": False, # Whether the payment is completed
        "service_type": "",   # Type of service (e.g., one-way, round-trip, airport)
        "flight_number": "",  # Flight number (if applicable)
        "train_number": "",   # International train number (if applicable)
        "created_at": ""      # Booking creation timestamp
    })

    # Payments Collection
    payments_collection = db["payments"]
    payments_collection.insert_one({
        "payment_id": None,   # Auto-generated unique identifier
        "booking_id": None,  # Reference to Bookings collection
        "amount": 0.0,       # Payment amount
        "payment_date": "", # Payment date
        "payment_method": "" # Method (e.g., Credit Card, PayPal)
    })

    # Schedules Collection
    schedules_collection = db["schedules"]
    schedules_collection.insert_one({
        "schedule_id": None, # Auto-generated unique identifier
        "driver_id": None,  # Reference to Drivers collection
        "car_id": None,     # Reference to Cars collection
        "date": "",       # Schedule date
        "time": ""        # Schedule time
    })

    print("Collections and schema created successfully!")

if __name__ == "__main__":
    create_collections()

 