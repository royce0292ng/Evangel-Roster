import csv
import sqlite3
import calendar
from datetime import datetime, timedelta

# Constants
DATABASE = "nurse_schedule.db"
conn = None
SHIFT_GROUPS = {
    "A": -1,
    "B": 1,
    "C": -1
}

# Connect to the database
def create_connection():
    global conn
    conn = sqlite3.connect(DATABASE)

# Disconnect from the database
def close_connection():
    global conn
    if conn:
        conn.close()

# Create the table
def create_tables():
    sql_create_nurses_table = """
    CREATE TABLE IF NOT EXISTS nurses (
        nurse_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT ,
        group_name TEXT NOT NULL
    );
    """
    sql_create_schedule_table = """
    CREATE TABLE IF NOT EXISTS schedule (
        nurse_id INTEGER NOT NULL,
        shift_date DATE NOT NULL,
        shift_type TEXT NOT NULL,
        PRIMARY KEY (nurse_id, shift_date),
        FOREIGN KEY (nurse_id) REFERENCES nurses (id)
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql_create_nurses_table)
        cursor.execute(sql_create_schedule_table)
    except sqlite3.Error as e:
        print(e)

# Add a nurse to the database
def add_nurse( name, group_name):

    sql_insert_nurse = """
    INSERT INTO nurses (name, group)
    VALUES (?, ?);
    """
    cursor = conn.cursor()
    cursor.execute(sql_insert_nurse, (name, group_name))
    conn.commit()

# Get all nurses from the database
def get_all_nurses():
    sql_select_nurses = "SELECT * FROM nurses;"
    cursor = conn.cursor()
    cursor.execute(sql_select_nurses)
    return cursor.fetchall()

# Load csv file
def load_csv(csvfile):
    """Initializes the CSV file with empty shift structure."""
    roster = []
    with open(csvfile, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            roster.append(row)
    return roster

def fetch_shifts_from_db(start_date, end_date):
    """
    Fetch shifts within a date range from the database.

    Parameters:
        db_path (str): Path to the SQLite database file.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        list of dict: Shift data with employee_id, date, and shift information.
    """
    # Connect to the SQLite database
    cursor = conn.cursor()

    # SQL query to select shifts within the date range
    query = """
    SELECT nurse_id, shift_date, shift_type 
    FROM schedule
    WHERE shift_date BETWEEN ? AND ?
    ORDER BY shift_date;
    """

    # Execute query with start_date and end_date as parameters
    cursor.execute(query, (start_date, end_date))

    # Fetch all results and format them as a list of dictionaries
    shifts = [
        {"nurse_id": row[0], "shift_date": row[1], "shift_type": row[2]}
        for row in cursor.fetchall()
    ]

    return shifts

def import_calendar_from_csv(file_path):
    calendar_data = []

    with open(file_path, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)

        # Read the month and year from the first row
        month_year = next(reader)
        month_name = month_year[0]  # Get the month name (e.g., "Jul")

        # Create a mapping of days of the week
        days_of_week = next(reader)[1:]  # Skip the first column and get the rest

        # Read the shifts data
        for row in reader:
            if row:  # Check if the row is not empty
                employee_id = row[0]
                shifts = row[1:]  # Get shifts, which correspond to the days

                for i, shift in enumerate(shifts):
                    if shift:  # Check if there is a shift
                        day = i + 1  # Day of the month
                        date_str = f"{month_name} {day} 2024"  # Assuming the year is 2024
                        date_obj = datetime.strptime(date_str, '%b %d %Y')  # Convert to datetime

                        calendar_data.append({
                            "employee_id": employee_id,
                            "date": date_obj.strftime("%Y-%m-%d"),
                            "shift": shift
                        })

    return calendar_data

def export_shifts_to_csv( start_date, end_date, output_file):
    """
    Export shift data within a specified date range to a CSV file.

    Parameters:
        shift_data (list): List of shift dictionaries with keys: "employee_id", "date", and "shift".
        start_date (str): Start date in the format "YYYY-MM-DD".
        end_date (str): End date in the format "YYYY-MM-DD".
        output_file (str): Output CSV file path.
    """

    # Convert start and end dates to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Filter shift data within the date range
    filtered_data = [
        shift for shift in shift_data
        if start_date <= datetime.strptime(shift["date"], "%Y-%m-%d") <= end_date
    ]

    # Sort the data by employee_id and then by date for a clean output
    filtered_data.sort(key=lambda x: (x["employee_id"], x["date"]))

    # Export to CSV
    with open(output_file, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Employee ID", "Date", "Shift"])  # Write header row

        for shift in filtered_data:
            writer.writerow([shift["employee_id"], shift["date"], shift["shift"]])

    print(f"Shift data exported to {output_file}")

def display_calendar_shifts(month, year):
    """
    Display employee shifts in a calendar format for a specific month and year.

    Parameters:
        shift_data (list): List of shift dictionaries with keys: "employee_id", "date", and "shift".
        month (int): The month to display (1 for January, 2 for February, etc.).
        year (int): The year to display.
    """

    shift_data = fetch_shifts_from_db('2024-07-1', '2024-07-31')

    # Filter shift data for the specified month and year
    month_shifts = [
        shift for shift in shift_data
        if datetime.strptime(shift["date"], "%Y-%m-%d").month == month and
           datetime.strptime(shift["date"], "%Y-%m-%d").year == year
    ]

    # Initialize a dictionary to store shifts by date
    shifts_by_date = {}
    for shift in month_shifts:
        date = datetime.strptime(shift["date"], "%Y-%m-%d").day
        if date not in shifts_by_date:
            shifts_by_date[date] = []
        shifts_by_date[date].append(f"{shift['employee_id']}:{shift['shift']}")

    # Print the calendar header
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    print(f"\n{month_name} {year}".center(30))
    print("Mon  Tue  Wed  Thu  Fri  Sat  Sun")

    # Display each week
    for week in cal:
        week_display = ""
        for day in week:
            if day == 0:
                week_display += "     "  # Empty space for days outside the month
            else:
                # Format the shift display for each day
                shifts = "\n".join(shifts_by_date.get(day, [" "]))[:5]  # Show up to 5 chars for simplicity
                week_display += f"{day:2} {shifts:5} "
        print(week_display)


# # Example usage
# print(SHIFT_GROUPS["A"])  # Output: -1
# conn = create_connection("nurse_schedule.db")
# create_tables(conn)
# file_path = 'calendar.csv'  # Replace with your actual file path
# calendar_shifts = import_calendar_from_csv(file_path)
#
# # Display the imported data
# for entry in calendar_shifts:
#     print(entry)
#
# # Example usage:
# shift_data = [
#     {"employee_id": "001", "date": "2024-07-01", "shift": "PH"},
#     {"employee_id": "001", "date": "2024-07-02", "shift": "AL"},
#     {"employee_id": "002", "date": "2024-07-05", "shift": "EC"},
#     {"employee_id": "003", "date": "2024-07-05", "shift": "O"},
#     # Add more sample shifts as needed
# ]
#
# export_shifts_to_csv(shift_data, "2024-07-01", "2024-07-07", "exported_shifts.csv")

