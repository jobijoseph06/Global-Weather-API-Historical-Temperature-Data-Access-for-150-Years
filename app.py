from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load station data
stations = pd.read_csv("data_small/stations.txt", skiprows=17)
stations = stations[["STAID", "STANAME                                 "]]


@app.route("/", methods=["GET", "POST"])
def home():
    result_html = ""
    if request.method == "POST":
        station_id = request.form.get("station")
        day = request.form.get("day")
        month = request.form.get("month")
        year = request.form.get("year")

        # Construct filename
        filename = f"data_small/TG_STAID{str(station_id).zfill(6)}.txt"
        try:
            df = pd.read_csv(filename, skiprows=20, parse_dates=['    DATE'])

            # Replace -9999 with NaN
            df['   TG'] = df['   TG'].replace(-9999, pd.NA)

            # Filter based on date
            if day and month and year:
                date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                temperature = df.loc[df['    DATE'] == date]['   TG'].squeeze()

                # Check for missing or invalid temperature
                if pd.isna(temperature):
                    result_html = f"<p class='text-warning'>No temperature data available for {date} at station {station_id}.</p>"
                else:
                    temperature = temperature / 10  # Convert to Celsius
                    result_html = f"<p class='text-success'>Temperature on {date} at station {station_id} is {temperature}°C.</p>"
            elif year:  # Filter by year
                df["    DATE"] = df["    DATE"].astype(str)
                yearly_data = df[df["    DATE"].str.startswith(year)]
                result_html = yearly_data.to_html(classes="table table-bordered", index=False)
            else:
                result_html = "<p class='text-danger'>Please provide complete date information.</p>"
        except FileNotFoundError:
            result_html = f"<p class='text-danger'>Data for station {station_id} not found.</p>"

    return render_template("home.html", stations=stations.to_dict(orient="records"), result_html=result_html)


app.run(debug=True)
