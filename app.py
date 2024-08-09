import pickle
from flask import request, Flask, render_template, redirect, url_for, flash
import matplotlib.pyplot as plt
import pandas as pd
# import all packages------------------------------------------
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import pickle

# Create an app------------------------------------------------
app = Flask(__name__)

# database configuration---------------------------------------
app.secret_key = "Secret Key"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/coviddb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define your model class for the Signin Tabel
class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    confirm_password = db.Column(db.String(100), nullable=False)

# Define your model class for the Signin Tabel
class employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)

# ======================================loading models and datasets================================
final_df = pd.read_csv('models/final_df.csv')
death_pipe = pickle.load(open('models/rf_pipe.pkl','rb'))
cases_pipe = pickle.load(open('models/rf_pipe_cases.pkl','rb'))

# ======================================dashboard functions========================================
def get_statistics(df):
    # Total deaths and total cases
    total_deaths = df['death_count'].sum()
    total_cases = df['cases_count'].sum()

    # Average duration based on years
    df['date'] = pd.to_datetime(df['date'])
    min_year = df['date'].dt.year.min()
    max_year = df['date'].dt.year.max()
    years_duration = max_year - min_year + 1  # Adding 1 to include both min and max years

    # County length
    county_len = len(df)

    # Additional insights
    # Average deaths per year
    avg_deaths_per_year = total_deaths / years_duration

    # Average cases per month
    avg_cases_per_month = total_cases / (county_len / 12)  # Assuming each record represents a month

    # More insights can be added based on the dataset

    # Return the statistics as separate variables
    return total_deaths, total_cases, years_duration, county_len, avg_deaths_per_year, avg_cases_per_month

#=====================prediction function====================================================


# Define the pred function
def pred_death(features_df):
    deaths = death_pipe.predict(features_df)
    return deaths[0]

# Define the pred function
def pred_cases(features_df):
    cases = cases_pipe.predict(features_df)
    return cases[0]

# routes===================================================================

@app.route('/')
def index():
    return render_template("index.html")





@app.route('/ana')
def ana():
    # Example usage:
    total_deaths, total_cases, years_duration, county_len, avg_deaths_per_year, avg_cases_per_month = get_statistics(
        final_df)
    return render_template("ana.html",df= final_df.head(20),total_deaths=total_deaths,total_cases=total_cases,years_duration=years_duration,
                           county_len=county_len,avg_deaths_per_year=avg_deaths_per_year,avg_cases_per_month=avg_cases_per_month)

@app.route('/covid_prediction')
def covid_prediction():
    return render_template("covid_prediction.html")

@app.route('/index')
def home():
    return render_template("index.html")
@app.route('/job')
def job():
    return render_template('job.html')


@app.route('/hrpage')
def hrpage():
    # Render the template with the path to the saved plot
    return render_template('hrpage.html')

@app.route('/emppage')
def emppage():
    return render_template('emppage.html')
@app.route('/td')
def td():
    return render_template('td.html')
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/hranalytic')
def hranalytic():
    return render_template('hranalytic.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/companypolicy')
def companypolicy():
    return render_template('companypolicy.html')

@app.route('/empleave')
def empleave():
    return render_template('empleave.html')

@app.route('/emplist')
def emplist():
    # Query all employees from the database
    employees = employee.query.all()
    return render_template('emplist.html', employees=employees)



@app.route('/eventspage')
def eventspage():
    return render_template('eventspage.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/empsettings')
def empsettings():
    return render_template('empsettings.html')


@app.route('/add_emp', methods=['POST'])
def add_emp():
    if request.method == 'POST':
        name = request.form.get('employeeName')
        department = request.form.get('employeeDepartment')

        # Check if name or department is empty
        if not name or not department:
            return render_template('emplist.html', message="Please fill in both name and department fields.")

        # Create a new employee object and add it to the database
        new_employee = employee(name=name, department=department)
        db.session.add(new_employee)
        db.session.commit()

        # Redirect to the employee list page after adding the employee
        return redirect(url_for('emplist'))
    else:
        return render_template('emplist.html', message="There was an error while adding employee.........")

@app.route('/remove_emp/<int:emp_id>', methods=['POST'])
def remove_emp(emp_id):
    # Find the employee to remove by their ID
    emp_to_remove = employee.query.get_or_404(emp_id)

    # Delete the employee from the database
    db.session.delete(emp_to_remove)
    db.session.commit()

    # Redirect back to the employee list page after removal
    return redirect(url_for('emplist'))


@app.route('/submit_registration', methods=['POST'])
def submit_registration():
    if request.method == 'POST':
        username = request.form['username']
        department = request.form['department']
        fullname = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            return render_template('register.html',message="Password not matching....")

        # Create a new Register object and add it to the database
        new_registration = Register(
            username=username,
            department=department,
            fullname=fullname,
            email=email,
            password=password,
            confirm_password=confirm_password
        )
        db.session.add(new_registration)
        db.session.commit()

        return render_template('hrpage.html')

    else:
        return redirect(url_for('please register'))

@app.route('/signin', methods=['POST'])
def submit_signin():
    if request.method == 'POST':
        username = request.form.get('username')  # Using .get() to handle cases where the field is empty
        password = request.form.get('password')  # Using .get() to handle cases where the field is empty

        # Check if username or password is empty
        if not username or not password:
            return render_template('index.html', message="Please fill in both username and password fields.")

        # Check if user exists in the register table
        user = Register.query.filter_by(username=username, password=password).first()

        if user:
            return render_template('hrpage.html')
        else:
            return render_template('index.html', message="Invalid username or password. Please try again.")
    else:
        return render_template('index.html', message="Invalid request. Please try again.")



@app.route('/predict', methods=['POST','GET'])
def predict():
    if request.method=="POST":
        # Get form data
        county_fips = int(request.form['countyFips'])
        county_name = request.form['countyName']
        state = request.form['state']
        statefip = int(request.form['statefip'])
        hosp_fips_code = float(request.form['hospFipsCode'])
        hosp_county_population = float(request.form['hospCountyPopulation'])
        vac_recip_county = request.form['vacRecipCounty']
        recip_state = request.form['recipState']
        administered_dose = float(request.form['administeredDose'])
        rur_fips = float(request.form['rurFips'])
        rur_population = float(request.form['rurPopulation'])
        day = int(request.form['day'])
        month = int(request.form['month'])
        year = int(request.form['year'])

        # Create a dataframe with the provided features
        features_df = pd.DataFrame({
            'county_fips': [county_fips],
            'county_name': [county_name],
            'state': [state],
            'state_fips': [statefip],  # Changed column name to 'state_fips'
            'hosp_fips_code': [hosp_fips_code],
            'hosp_county_population': [hosp_county_population],
            'Vac_Recip_County': [vac_recip_county],
            'Recip_State': [recip_state],
            'Administered_Dose1_Recip': [administered_dose],
            'Rur_FIPS': [rur_fips],
            'Rur_Population': [rur_population],
            'day': [day],
            'month': [month],
            'year': [year]
        })

        # Make prediction
        predicted_deaths = pred_death(features_df)
        predicted_cases = pred_cases(features_df)

        return render_template('covid_prediction.html', predicted_deaths=int(predicted_deaths),
                               predicted_cases=int(predicted_cases))

# ========================python main===================================================
if __name__ == "__main__":

    app.run(debug=True)
