import numpy as np
import datetime as dt
from datetime import datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, request


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station=Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/date/enter-a-date<br/>"
        f"/api/v1.0/dates/enter-a-start-date/enter-an-end-date<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation values for the whole last 12 months"""
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    one_year_data = session.query(Measurement.station,Measurement.prcp).\
    filter(Measurement.date <= dt.date(2017, 8, 23)).\
    filter(Measurement.date>= year_ago).\
    order_by(Measurement.date).all()
    session.close()
    # Convert list of tuples into normal list
    all = []
    for station, prcp in one_year_data:
        station_dict = {}
        station_dict["station name"] = station
        station_dict["precipitation"] = prcp
        all.append(station_dict)
    
    return jsonify(all)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations=session.query(Measurement.station,func.count(Measurement.date)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.date).desc()).all()
    session.close()
    all_values = list(np.ravel(stations))
    return jsonify(all_values)

@app.route("/api/v1.0/tobs")
def temp():
    station_id='USC00519281'
    session = Session(engine)
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results=session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date <= dt.date(2017, 8, 23)).\
    filter(Measurement.date>= year_ago).\
    filter(Measurement.station == station_id).all()
    session.close()
    all_values = list(np.ravel(results))
    return jsonify(all_values)

@app.route("/api/v1.0/date/<start>")
def start(start):
    session = Session(engine)
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()
    session.close()
    all_values = list(np.ravel(results))
    return jsonify(all_values)

@app.route("/api/v1.0/dates/<start>/<end>")
def start_end(start,end):
    session = Session(engine)
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()
    session.close()
    all_values = list(np.ravel(results))
    return jsonify(all_values)

if __name__ == '__main__':
    app.run(debug=True)