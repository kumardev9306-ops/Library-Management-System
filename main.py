
# Database connection function ko import kar rahe hain
from database import connect_db

# Dashboard open karne wala function import kar rahe hain
from dashboard import create_dashboard


# Sabse pehle database connection check kar rahe hain
db = connect_db()


# Agar database successfully connect ho gaya
if db:

    # Test connection ko close kar rahe hain
    # Dashboard apna alag connection use karega
    db.close()

    # Dashboard start pythphone se pehle message show hoga
    print("Starting Library Management System...")

    # Main dashboard window open kar rahe hain
    create_dashboard()


else:

    # Agar database connect nahi hua toh ye message show hoga
    print("Please check your MySQL connection.")
