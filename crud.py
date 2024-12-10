import streamlit as st
from pymongo import MongoClient
import pandas as pd
import bson
from datetime import datetime, date  # Ensure both datetime and date are imported

import hashlib
import re
import uuid

# MongoDB Connection
CONNECTION_STRING = "mongodb+srv://shreyashestabit:Nuvac#3462@cluster0.m8wzm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(CONNECTION_STRING)
db = client["car_booking_system"]

def generate_system_id(collection):
    """Generate a unique incremental ID for a collection."""
    try:
        last_doc = list(collection.find().sort('_id', -1).limit(1))
        if last_doc:
            # Find the ID field (assuming the second field is the ID field)
            id_field_name = [field['name'] for field in schemas[collection.name] if field['name'].endswith('_id')][0]
            
            # Get the last ID value, defaulting to 0 if not found
            last_id = last_doc[0].get(id_field_name, 0)
            
            # Safely convert to integer, handling potential string/non-numeric values
            try:
                last_id = int(last_id) if last_id is not None else 0
            except (ValueError, TypeError):
                last_id = 0
            
            return last_id + 1
        return 1  # Start with 1 if no documents exist
    except Exception as e:
        st.error(f"Error generating system ID: {e}")
        return 1

def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Validate email format."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# List of Collections (Tables)
collections = {
    "Corporate Clients": db["corporate_clients"],
    "Users": db["users"],
    "Cars": db["cars"],
    "Drivers": db["drivers"],
    "Bookings": db["bookings"],
    "Payments": db["payments"],
    "Schedules": db["schedules"],
}

# Schema for each collection with field types and input methods
schemas = {
    "Corporate Clients": [
        {"name": "corporate_id", "type": int, "input_type": "system_generated"},
        {"name": "company_name", "type": str, "input_type": "text"},
        {"name": "email", "type": str, "input_type": "email"},
        {"name": "phone", "type": str, "input_type": "phone"},
        {"name": "password_hash", "type": str, "input_type": "password"},
        {"name": "created_at", "type": datetime, "input_type": "system_generated"}
    ],
    "Users": [
        {"name": "user_id", "type": int, "input_type": "system_generated"},
        {"name": "name", "type": str, "input_type": "text"},
        {"name": "email", "type": str, "input_type": "email"},
        {"name": "phone", "type": str, "input_type": "phone"},
        {"name": "password_hash", "type": str, "input_type": "password"},
        {"name": "user_type", "type": str, "input_type": "select", "options": ["individual", "corporate"]},
        {"name": "corporate_id", "type": int, "input_type": "number", "optional": True},
        {"name": "created_at", "type": datetime, "input_type": "system_generated"}
    ],
    "Cars": [
        {"name": "car_id", "type": int, "input_type": "system_generated"},
        {"name": "model", "type": str, "input_type": "text"},
        {"name": "type", "type": str, "input_type": "select", "options": ["sedan", "suv", "luxury", "compact"]},
        {"name": "license_plate", "type": str, "input_type": "text"},
        {"name": "capacity", "type": int, "input_type": "number"},
        {"name": "rate_per_km", "type": float, "input_type": "number"}
    ],
    "Drivers": [
        {"name": "driver_id", "type": int, "input_type": "system_generated"},
        {"name": "name", "type": str, "input_type": "text"},
        {"name": "driver_license", "type": str, "input_type": "text"},
        {"name": "phone", "type": str, "input_type": "phone"},
        {"name": "experience", "type": int, "input_type": "number"},
        {"name": "assigned_car_id", "type": int, "input_type": "number", "optional": True}
    ],
    "Bookings": [
        {"name": "booking_id", "type": int, "input_type": "system_generated"},
        {"name": "user_id", "type": int, "input_type": "number"},
        {"name": "car_id", "type": int, "input_type": "number"},
        {"name": "driver_id", "type": int, "input_type": "number"},
        {"name": "booking_date", "type": datetime, "input_type": "date"},
        {"name": "start_time", "type": str, "input_type": "time"},
        {"name": "end_time", "type": str, "input_type": "time"},
        {"name": "total_price", "type": float, "input_type": "number"},
        {"name": "payment_status", "type": bool, "input_type": "checkbox"},
        {"name": "service_type", "type": str, "input_type": "select", "options": ["airport", "train", "local"]},
        {"name": "flight_number", "type": str, "input_type": "text", "optional": True},
        {"name": "train_number", "type": str, "input_type": "text", "optional": True},
        {"name": "created_at", "type": datetime, "input_type": "system_generated"}
    ],
    "Payments": [
        {"name": "payment_id", "type": int, "input_type": "system_generated"},
        {"name": "booking_id", "type": int, "input_type": "number"},
        {"name": "amount", "type": float, "input_type": "number"},
        {"name": "payment_date", "type": datetime, "input_type": "date"},
        {"name": "payment_method", "type": str, "input_type": "select", "options": ["credit_card", "debit_card", "bank_transfer", "cash"]}
    ],
    "Schedules": [
        {"name": "schedule_id", "type": int, "input_type": "system_generated"},
        {"name": "driver_id", "type": int, "input_type": "number"},
        {"name": "car_id", "type": int, "input_type": "number"},
        {"name": "date", "type": datetime, "input_type": "date"},
        {"name": "time", "type": str, "input_type": "time"}
    ]
}

def insert_record(collection, schema):
    st.subheader(f"Insert New Record into {collection.name}")
    
    form_data = {}
    errors = []
    
    # Generate input fields based on the schema
    for field in schema:
        # Skip system-generated fields
        if field['input_type'] == 'system_generated':
            continue
        
        # Handle optional fields
        if field.get('optional', False):
            include_optional = st.checkbox(f"Include {field['name']}")
            if not include_optional:
                continue
        
        # Create input based on input type
        try:
            if field['input_type'] == 'text':
                form_data[field['name']] = st.text_input(field['name'])
            elif field['input_type'] == 'email':
                email = st.text_input(field['name'], help="Enter a valid email address")
                if email:
                    if validate_email(email):
                        form_data[field['name']] = email
                    else:
                        errors.append(f"Invalid email format for {field['name']}")
            elif field['input_type'] == 'number':
                # Explicitly handle number input
                if field['type'] == int:
                    form_data[field['name']] = st.number_input(field['name'], min_value=0, step=1)
                elif field['type'] == float:
                    form_data[field['name']] = st.number_input(field['name'], min_value=0.0, step=0.01)
            elif field['input_type'] == 'phone':
                form_data[field['name']] = st.text_input(field['name'])
            elif field['input_type'] == 'password':
                form_data[field['name']] = st.text_input(field['name'], type='password')
            elif field['input_type'] == 'date':
                form_data[field['name']] = st.date_input(field['name'])
            elif field['input_type'] == 'time':
                form_data[field['name']] = st.time_input(field['name'])
            elif field['input_type'] == 'select':
                form_data[field['name']] = st.selectbox(field['name'], field['options'])
            elif field['input_type'] == 'checkbox':
                form_data[field['name']] = st.checkbox(field['name'])
        except Exception as e:
            errors.append(f"Error processing {field['name']}: {str(e)}")
    
    # Display any errors
    if errors:
        for error in errors:
            st.error(error)
        return
    
    if st.button("Insert Record"):
        try:
            # Add system-generated fields
            for field in schema:
                if field['input_type'] == 'system_generated':
                    if field['name'].endswith('_id'):
                        form_data[field['name']] = generate_system_id(collection)
                    elif field['name'] == 'created_at':
                        form_data[field['name']] = datetime.now()
                    elif field['name'] == 'password_hash':
                        # Hash password if applicable
                        if 'password' in form_data:
                            form_data[field['name']] = hash_password(form_data['password'])
                            del form_data['password']
            
            # Validate and convert data types
            validated_data = {}
            for field in schema:
                if field['name'] in form_data:
                    value = form_data[field['name']]
                    
                    # Type conversion with error handling
                    try:
                        if field['type'] == int:
                            validated_data[field['name']] = int(value) if value != '' else None
                        elif field['type'] == float:
                            validated_data[field['name']] = float(value) if value != '' else None
                        elif field['type'] == str:
                            validated_data[field['name']] = str(value) if value is not None else None
                        else:
                            validated_data[field['name']] = value
                    except ValueError as e:
                        st.error(f"Error converting {field['name']}: {e}")
                        return
            
            # Remove any None values
            validated_data = {k: v for k, v in validated_data.items() if v is not None}
            
            collection.insert_one(validated_data)
            st.success("Record inserted successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error during insertion: {e}")
            # Optional: Print full traceback for debugging
            import traceback
            st.error(traceback.format_exc())

def update_record(collection, schema):
    st.subheader(f"Update Record in {collection.name}")
    
    # Display existing records in a table
    documents = list(collection.find())
    if documents:
        # Convert ObjectId to string for display
        df = pd.DataFrame(documents).drop(columns="_id")
        df['_id'] = [str(doc['_id']) for doc in documents]
        st.dataframe(df)

        # Let user select a record to edit
        record_to_update = st.selectbox("Select Record to Edit", options=df['_id'].tolist())
        
        if record_to_update:
            try:
                # Convert string back to ObjectId
                record = collection.find_one({"_id": bson.ObjectId(record_to_update)})
                
                if record is None:
                    st.error("Selected record not found.")
                    return
                
                # Create a form to edit each field
                updated_data = {}
                for field in schema:
                    # Skip system-generated fields
                    if field['input_type'] == 'system_generated':
                        continue
                    
                    # Only process fields that exist in the record
                    if field['name'] in record:
                        # Handle different input types
                        # Add a unique key to each input element
                        unique_key = f"{record_to_update}_{field['name']}"
                        
                        if field['input_type'] == 'text':
                            updated_value = st.text_input(
                                field['name'], 
                                value=str(record[field['name']]) if record[field['name']] else "",
                                key=unique_key
                            )
                        elif field['input_type'] == 'email':
                            email = st.text_input(
                                field['name'], 
                                value=record[field['name']] or "", 
                                help="Enter a valid email address",
                                key=unique_key
                            )
                            if email and not validate_email(email):
                                st.error(f"Invalid email format for {field['name']}")
                                continue
                            updated_value = email
                        elif field['input_type'] == 'number':
                            updated_value = st.number_input(
                                field['name'], 
                                value=record[field['name']] or 0, 
                                min_value=0,
                                key=unique_key
                            )
                        elif field['input_type'] == 'date':
                            # Handle both datetime and date objects
                            current_date = record[field['name']]
                            if isinstance(current_date, datetime):
                                current_date = current_date.date()
                            
                            updated_value = st.date_input(
                                field['name'], 
                                value=current_date if current_date else date.today(),
                                key=unique_key
                            )
                        elif field['input_type'] == 'time':
                            # Convert to time if it's a datetime
                            current_time = record[field['name']]
                            if isinstance(current_time, datetime):
                                current_time = current_time.time()
                            
                            updated_value = st.time_input(
                                field['name'],
                                value=current_time,
                                key=unique_key
                            )
                        elif field['input_type'] == 'select':
                            updated_value = st.selectbox(
                                field['name'], 
                                field['options'], 
                                index=field['options'].index(record[field['name']]) 
                                    if record[field['name']] in field['options'] else 0,
                                key=unique_key
                            )
                        elif field['input_type'] == 'checkbox':
                            updated_value = st.checkbox(
                                field['name'], 
                                value=record[field['name']] or False,
                                key=unique_key
                            )
                        
                        # Only add to updated_data if the value has changed
                        if updated_value != record[field['name']]:
                            # Convert date to datetime for MongoDB compatibility
                            if isinstance(updated_value, date) and not isinstance(updated_value, datetime):
                                updated_value = datetime.combine(updated_value, datetime.min.time())
                            
                            updated_data[field['name']] = updated_value
                
                if st.button("Save Changes"):
                    if updated_data:
                        # Hash password if it's being updated
                        if 'password' in updated_data:
                            updated_data['password_hash'] = hash_password(updated_data['password'])
                            del updated_data['password']
                        
                        collection.update_one(
                            {"_id": bson.ObjectId(record_to_update)}, 
                            {"$set": updated_data}
                        )
                        st.success("Record updated successfully!")
                        st.rerun()
                    else:
                        st.warning("No changes made.")
            except Exception as e:
                st.error(f"Error updating record: {e}")
    else:
        st.info("No records found.")


# Delete Record Function
def delete_record(collection):
    st.subheader(f"Delete Record from {collection.name}")
    
    # Display existing records
    documents = list(collection.find())
    if documents:
        # Convert ObjectId to string for display
        
        df = pd.DataFrame(documents).drop(columns="_id")
        df['_id'] = [str(doc['_id']) for doc in documents]
        st.dataframe(df)

        record_to_delete = st.selectbox("Select Record to Delete", options=df['_id'].tolist())
        
        if st.button("Delete Selected Record"):
            try:
                collection.delete_one({"_id": bson.ObjectId(record_to_delete)})
                st.success("Record deleted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("No records found.")

# Streamlit App Configuration
st.set_page_config(page_title="CRUD Operations", layout="wide")
st.sidebar.title("Tables")

# Sidebar: Select Collection
table_selected = st.sidebar.radio("Select a Table to Manage", list(collections.keys()))
selected_collection = collections[table_selected]
selected_schema = schemas[table_selected]

# Main Interface
st.title(f"Manage {table_selected}")

# Tabs for CRUD Operations
tab1, tab2, tab3, tab4 = st.tabs(["View", "Insert", "Update", "Delete"])

with tab1:
    # View: Show the collection records
    documents = list(selected_collection.find())
    if documents:
        df = pd.DataFrame(documents).drop(columns="_id")
        st.dataframe(df)
    else:
        st.info("No records found.")

with tab2:
    insert_record(selected_collection, selected_schema)

with tab3:
    update_record(selected_collection, selected_schema)

with tab4:
    delete_record(selected_collection)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("CRUD App for MongoDB - Built with Streamlit")
