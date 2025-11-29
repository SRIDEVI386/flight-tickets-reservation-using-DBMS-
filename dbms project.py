import mysql.connector
from datetime import datetime

# Connect to MySQL Database
con = mysql.connector.connect(
    host="localhost",
    user="root",              # your MySQL username
    password="sridevi@386", # your MySQL password
    database="flight_reservation"
)
cursor = con.cursor()

# -------------------------------
# VIEW AVAILABLE FLIGHTS
# -------------------------------
def view_flights():
    cursor.execute("SELECT * FROM Flights")
    flights = cursor.fetchall()
    print("\n--- Available Flights ---")
    for f in flights:
        print(f"ID: {f[0]} | Airline: {f[1]} | From: {f[2]} -> {f[3]} | Departure: {f[4]} | Price: ₹{f[8]}")
    print("--------------------------")

# -------------------------------
# ADD NEW PASSENGER
# -------------------------------
def add_passenger():
    name = input("Enter passenger name: ")
    age = int(input("Enter age: "))
    gender = input("Enter gender (Male/Female): ")
    contact = input("Enter contact number: ")
    email = input("Enter email: ")

    query = "INSERT INTO Passengers (name, age, gender, contact, email) VALUES (%s, %s, %s, %s, %s)"
    values = (name, age, gender, contact, email)
    cursor.execute(query, values)
    con.commit()
    print("✅ Passenger added successfully!")

# -------------------------------
# BOOK A FLIGHT
# -------------------------------
def book_ticket():
    try:
        passenger_id = int(input("Enter passenger ID: "))
        flight_id = int(input("Enter flight ID: "))
    except ValueError:
        print("❌ Passenger ID and Flight ID must be integers!")
        return

    # Check if passenger exists
    cursor.execute("SELECT * FROM Passengers WHERE passenger_id = %s", (passenger_id,))
    passenger = cursor.fetchone()
    if not passenger:
        print("❌ Passenger not found!")
        return

    # Check flight availability
    cursor.execute("SELECT available_seats, price FROM Flights WHERE flight_id = %s", (flight_id,))
    flight = cursor.fetchone()
    if not flight:
        print("❌ Flight not found!")
        return

    available_seats, price = flight
    if available_seats <= 0:
        print("❌ No seats available for this flight.")
        return

    seat_no = available_seats  # assign last available seat
    booking_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert ticket
    cursor.execute(
        "INSERT INTO Tickets (passenger_id, flight_id, seat_no, status, booking_date) VALUES (%s, %s, %s, %s, %s)",
        (passenger_id, flight_id, seat_no, "Booked", booking_date)
    )
    ticket_id = cursor.lastrowid

    # Update flight seats
    cursor.execute(
        "UPDATE Flights SET available_seats = available_seats - 1 WHERE flight_id = %s", (flight_id,)
    )

    # Insert payment record
    cursor.execute(
        "INSERT INTO Payments (ticket_id, amount, mode, status, date) VALUES (%s, %s, %s, %s, %s)",
        (ticket_id, price, "Card", "Success", booking_date)
    )

    # Commit all changes
    con.commit()

    print(f"🎟️ Ticket booked successfully! Ticket ID: {ticket_id} | Seat No: {seat_no}")


# -------------------------------
# CANCEL A TICKET
# -------------------------------
def cancel_ticket():
    ticket_id = int(input("Enter Ticket ID to cancel: "))
    cursor.execute("SELECT flight_id, status FROM Tickets WHERE ticket_id = %s", (ticket_id,))
    ticket = cursor.fetchone()

    if not ticket:
        print("❌ Ticket not found!")
        return

    flight_id, status = ticket
    if status == "Cancelled":
        print("⚠️ Ticket already cancelled!")
        return

    # Update ticket status
    cursor.execute("UPDATE Tickets SET status = 'Cancelled' WHERE ticket_id = %s", (ticket_id,))
    # Update flight seat count
    cursor.execute("UPDATE Flights SET available_seats = available_seats + 1 WHERE flight_id = %s", (flight_id,))
    # Update payment status
    cursor.execute("UPDATE Payments SET status = 'Refunded' WHERE ticket_id = %s", (ticket_id,))
    con.commit()

    print("❌ Ticket cancelled and payment refunded!")

# -------------------------------
# VIEW ALL BOOKINGS
# -------------------------------
def view_bookings():
    cursor.execute("""
        SELECT t.ticket_id, p.name, f.airline, f.source, f.destination, t.status, t.booking_date
        FROM Tickets t
        JOIN Passengers p ON t.passenger_id = p.passenger_id
        JOIN Flights f ON t.flight_id = f.flight_id
    """)
    bookings = cursor.fetchall()
    print("\n--- All Bookings ---")
    for b in bookings:
        print(f"Ticket ID: {b[0]} | Passenger: {b[1]} | Airline: {b[2]} | From {b[3]} to {b[4]} | Status: {b[5]} | Date: {b[6]}")
    print("--------------------")

# -------------------------------
# MAIN MENU
# -------------------------------
def main():
    while True:
        print("""
================= FLIGHT RESERVATION SYSTEM =================
1. View Flights
2. Add Passenger
3. Book Ticket
4. Cancel Ticket
5. View All Bookings
6. Exit
==============================================================
""")
        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            view_flights()
        elif choice == "2":
            add_passenger()
        elif choice == "3":
            book_ticket()
        elif choice == "4":
            cancel_ticket()
        elif choice == "5":
            view_bookings()
        elif choice == "6":
            print("👋 Exiting System...")
            break
        else:
            print("❌ Invalid choice! Please try again.")

if __name__ == "__main__":
    main()
    cursor.close()
    con.close()
