from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="such@2005",
    database="emp_db"
)

cursor = db.cursor()


class Employee:
    def __init__(self, name, dept, salary_per_day):
        self.name = name
        self.dept = dept
        self.salary_per_day = salary_per_day

class Payroll:
    def calculate_salary(self, days, salary_per_day):
        return days * salary_per_day



@app.route("/")
def home():
    return render_template("home.html")


# Add Employee
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        emp = Employee(
            request.form["name"],
            request.form["dept"],
            request.form["salary"]
        )

        sql = "INSERT INTO employee(name, dept, salary_per_day) VALUES (%s, %s, %s)"
        cursor.execute(sql, (emp.name, emp.dept, emp.salary_per_day))
        db.commit()

        return "<script>alert('Employee Added Successfully!'); window.location='/view';</script>"

    return render_template("add.html")


# View Employees
@app.route("/view")
def view():
    cursor.execute("SELECT * FROM employee")
    data = cursor.fetchall()
    return render_template("view.html", data=data)


# Mark Attendance
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if request.method == "POST":
        emp_id = request.form["emp_id"]
        date = request.form["date"]
        status = request.form["status"]

        sql = "INSERT INTO attendance(emp_id, date, status) VALUES (%s, %s, %s)"
        cursor.execute(sql, (emp_id, date, status))
        db.commit()

        return redirect("/view_attendance")

    return render_template("attendance.html")


# View Attendance
@app.route("/view_attendance")
def view_attendance():
    cursor.execute("""
        SELECT employee.name, attendance.date, attendance.status
        FROM attendance
        JOIN employee ON employee.emp_id = attendance.emp_id
    """)
    data = cursor.fetchall()
    return render_template("view_attendance.html", data=data)


# Salary Calculation (Simple Logic)
@app.route("/salary/<int:emp_id>")
def salary(emp_id):
    cursor.execute("SELECT salary_per_day FROM employee WHERE emp_id=%s", (emp_id,))
    salary_per_day = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE emp_id=%s AND status='Present'
    """, (emp_id,))
    days = cursor.fetchone()[0]

    payroll = Payroll()
    total_salary = payroll.calculate_salary(days, salary_per_day)

    return f"Employee ID {emp_id} Salary = {total_salary}"


if __name__ == "__main__":
    app.run(debug=True)