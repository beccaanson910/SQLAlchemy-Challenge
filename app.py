# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(autoload_with = engine)

# Save references to each table

Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """"Start at the homepage"""
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/type_start_date<br/>"
        f"/api/v1.0/type_start_date/type_end_date"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #Query needed precipitation data
    query = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= '2016-08-23').all()

    session.close()

    #Convert to a dictionary
    all_precip = []
    for date, prcp in query:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        all_precip.append(precip_dict)

    #jsonify results
    return jsonify(all_precip)


@app.route("/api/v1.0/station")
def station():

    """Return a list of all the stations"""
    # Query all the stations
    results = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Create a dictionary and append to the list of stations

    all_names = []
    for id, staion, name, latitude, longitude, elevation in results:
        station_dict = {}

        station_dict['Id'] = id
        station_dict['station'] = station
        station_dict['name'] = name
        station_dict['latitude'] = latitude
        station_dict['longitude'] = longitude
        station_dict['elevation'] = elevation

        all_names.append(station_dict)

    #jsonify results
    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    #Query tobs data
    observed_temp = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= '2016-08-18').all()
    
    session.close()
    
    # Convert list of tuples into normal list
    all_temps = list(np.ravel(observed_temp))

    #jsonify results
    return jsonify(all_temps)

@app.route("/api/v1.0/<start>")
def date(start):
    #set start date
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")

    temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    
    session.close()
  
    # Convert into a normal list
    temperature_range = list(np.ravel(temperature_data))

    #jsonify results
    return jsonify(temperature_range)


@app.route("/api/v1.0/<start>/<end>")
def date_ranges(start,end):
    #set the start and end dates
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")


    #calculate the minimum, maximum, & avgerage, temperatures based on the date ranges
    temperature_range = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    
    session.close()
    
    # Convert into a normal list
    temperature_values = list(np.ravel(temperature_range))

    #jsonify results
    return jsonify(temperature_values)


if __name__ == '__main__':
    app.run(debug=True)