import csv
import os

from data import *

# Constants
CSV_FILE = "Data/Roster - Sample 1.csv"

# Function to load roster data from CSV
def load_roster():
    roster = []
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            roster.append(row)
    return roster

def import_data():
    file_path = input("Enter the CSV file path to import: ")
    # Code to import data goes here
    print("Data imported successfully.")

def add_shift():
    employee_id = input("Enter employee ID: ")
    date = input("Enter date (YYYY-MM-DD): ")
    shift_type = input("Enter shift type (e.g., morning, evening): ")
    # Code to add shift goes here
    print("Shift added successfully.")

def edit_shift():
    employee_id = input("Enter employee ID: ")
    date = input("Enter date of shift to edit (YYYY-MM-DD): ")
    new_shift_type = input("Enter new shift type: ")
    # Code to update shift here
    print("Shift updated successfully.")

def delete_shift():
    employee_id = input("Enter employee ID: ")
    date = input("Enter date of shift to delete (YYYY-MM-DD): ")
    # Code to delete shift here
    print("Shift deleted successfully.")

def view_roster():
    roster = load_roster()
    for row in roster:
        print(', '.join(row))
    print("Full roster displayed.")

def view_weekly_roster():
    start_date = input("Enter start date of the week (YYYY-MM-DD): ")
    # Code to display weekly roster goes here
    print("Weekly roster displayed.")

def view_monthly_roster():
    month = input("Enter month (e.g., 2024-07): ")
    # Code to display monthly roster goes here
    print("Monthly roster displayed.")

def add_employee():
    name = input("Enter employee name: ")
    group = input("Enter employee group: ")
    # Code to add employee here
    print(f"Employee {name} added to group {group}.")

def remove_employee():
    employee_id = input("Enter employee ID to remove: ")
    # Code to remove employee here
    print(f"Employee with ID {employee_id} removed.")

def exit_program():
    print("Exiting the system.")
    exit()

menu_options = {
        '0': exit_program,
        '1': import_data,
        '2': add_shift,
        '3': edit_shift,
        '4': delete_shift,
        '5': view_roster,
        '6': view_weekly_roster,
        '7': view_monthly_roster,
        '8': add_employee,
        '9': remove_employee,
        '10': exit_program
    }

# Main menu function
def main():

    create_connection()
    create_tables()

    while True:
        print("""
Roster Management System
0. Exit
1. Import Data
2. Export Data
3. Add Shift
4. Edit Shift
5. Delete Shift
6. View Roster
7. View Weekly Roster
8. View Monthly Roster
9. Add New Employee
10. Remove Employee

Choose an option (0-10):
                """)
        choice = input("Enter your choice: ")
        action = menu_options.get(choice)
        if action:
            action()  # Calls the respective function
        else:
            print("Invalid choice. Please choose again.")

    close_connection()


# Run the main function
if __name__ == "__main__":
    main()
