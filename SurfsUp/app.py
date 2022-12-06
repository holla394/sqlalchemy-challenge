import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start_date&gt;<br/>"
        f"/api/v1.0/&lt;start_date&gt;/&lt;end_date&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    with Session(engine) as session:
        # Find the most recent date in the data set.
        recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        print(recent_date)
        recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
        recent_date = recent_date.date()
        # Calculate the date one year from the last date in data set.
        last_date = recent_date - dt.timedelta(days=365)

        # Design a query to find the most active stations (i.e. what stations have the most rows?)
        active_stations = session.query(Station.station, func.count(Station.station))\
            .group_by(Station.station).order_by(func.count(Station.station).desc()).all()

        # List the stations and the counts in descending order.
        print(active_stations)
        most_active = active_stations[0][0]

        # Perform a query to retrieve the data and precipitation scores
        last12 = session.query(Measurement.date, Measurement.prcp)\
            .where(Measurement.date >= last_date, Measurement.station == most_active)\
                .all()

    # Convert list of tuples into normal list
    last12_dict = [dict(zip(row.keys(), row)) for row in last12]

    return jsonify(last12_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    with Session(engine) as session:
        # Perform a query
        stations_query = session.query(Station.station,\
            Station.latitude,\
                Station.longitude,\
                    Station.elevation)\
                        .all()

    stations_dict = [dict(zip(row.keys(), row)) for row in stations_query]
    return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    with Session(engine) as session:
        # Find the most recent date in the data set.
        recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        print(recent_date)
        recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
        recent_date = recent_date.date()
        # Calculate the date one year from the last date in data set.
        last_date = recent_date - dt.timedelta(days=365)

        # Design a query to find the most active stations (i.e. what stations have the most rows?)
        active_stations = session.query(Station.station, func.count(Station.station))\
            .group_by(Station.station).order_by(func.count(Station.station).desc()).all()

        # List the stations and the counts in descending order.
        print(active_stations)
        most_active = active_stations[0][0]

        # Perform a query to retrieve the date and tobs scores
        last12 = session.query(Measurement.date, Measurement.tobs)\
            .where(Measurement.date >= last_date, Measurement.station == most_active)\
                .all()

    # Convert list of tuples into normal list
    last12_dict = [dict(zip(row.keys(), row)) for row in last12]

    return jsonify(last12_dict)

# this is a decorator
@app.route("/api/v1.0/<start_date>")
def start_only(start_date):
    # end = request.args.get("end")

    with Session(engine) as session:
        # Design a query to find the most active stations (i.e. what stations have the most rows?)
        active_stations = session.query(Station.station, func.count(Station.station))\
            .group_by(Station.station).order_by(func.count(Station.station).desc()).all()

        # List the stations and the counts in descending order.
        most_active = active_stations[0][0]

        data = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
            where(Measurement.date >= start_date,\
                Measurement.station == most_active).\
                    all()

    min = data[0][0]
    max = data[0][1]
    avg = round(data[0][2], 2)
    # Convert list of tuples into normal list
    
    return jsonify({"Min temp":min,"Max temp":max,"Avg temp":avg})

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_and_end(start_date, end_date):

    with Session(engine) as session:
        # Design a query to find the most active stations (i.e. what stations have the most rows?)
        active_stations = session.query(Station.station, func.count(Station.station))\
            .group_by(Station.station).order_by(func.count(Station.station).desc()).all()

        # List the stations and the counts in descending order.
        most_active = active_stations[0][0]

        data = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
            where(Measurement.date >= start_date, Measurement.date <= end_date,\
                Measurement.station == most_active).\
                    all()

    min = data[0][0]
    max = data[0][1]
    avg = round(data[0][2], 2)
    # Convert list of tuples into normal list
    
    return jsonify({"Min temp":min,"Max temp":max,"Avg temp":avg})

if __name__ == '__main__':
    app.run(debug=True)
    