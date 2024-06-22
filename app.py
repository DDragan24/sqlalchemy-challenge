from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

# connect the the batabase
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflects existing database
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# save the references
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create Session
session = Session(engine)

# home route
@app.route("/")
def home():
    return(f"<center><h2>Welcome to the Hawaii Climate Analysis Local API!</h2></center>"
           f"<center><h3>Select from one of the available routes:</h3></center>"
           f"<center>/api/v1.0/precipitation</center>"
           f"<center>/api/v1.0/stations</center>"
           f"<center>/api/v1.0/tobs</center>"
           f"<center>/api/v1.0/start/end</center>"

           )

# /api/v1.0/precipitation Route
@app.route("/api/v1.0/precipitation")
def precip():
    # return previous year's precipitation as a json
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= previousYear).all()
    
    session.close()
    # dictionary with the date as the key and the precipitation (prcp) as the value
    precipitation = {date: prcp for date, prcp in results}
    # convert to json
    return jsonify(precipitation)


# /api/v1.0/stations Route
@app.route("/api/v1.0/stations")
def stations():
    # show a list of the stations
    # Perform a query to retrieve names of the stations
    results = session.query(Station.station).all()
    session.close()

    stationList = list(np.ravel(results))

    # convert tojson and display
    return jsonify(stationList)


# /api/v1.0/tobs Route
@app.route("/api/v1.0/tobs")
def temps():
    # return the previous Year
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017,8,23) - dt.timedelta(days=365)

    # perform querry to retrive temperatures from most active station from past year
    results = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= previousYear).all()
    session.close()

    tempList = list(np.ravel(results))
    # return the list of temps
    return jsonify(tempList)

# /api/v1.0/start/end and /api/v1.0/start Routes
@app.route("/api/v1.0/<start>") 
@app.route("/api/v1.0/<start>/<end>")
def dataStats(start=None, end=None):

    # select statement
    selection = [func.min[Measurement.tobs], func.max[Measurement.tobs], func.avg[Measurement.tobs]]

    if not end:
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*selection).filter(Measurement.date >= startDate).all()
        session.close()
        tempList = list(np.ravel(results))
    
        # return the list of temps
        return jsonify(tempList)
    
    startDate = dt.datetime.strptime(start, "%m%d%Y")
    endDate = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*selection)\
        .filter(Measurement.date >= startDate)\
        .filter(Measurement.date <= endDate).all()

    session.close()
    tempList = list(np.ravel(results))
    
        # return the list of temps
    return jsonify(tempList)

## app launcher
if __name__ == '__main__':
    app.run(debug=True)
