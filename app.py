# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def welcome():
    return(
        f"Weclome to the Hawaiian climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/2010-01-01<br/>"
        f"/api/v1.0/start/2010-01-01/end/2017-08-23"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():

    date_prcp = session.query(measurement.date, measurement.prcp).all()

    session.close()
    
    x = []
    for date, prcp in date_prcp:
        date_dict = {}
        date_dict[date] = prcp
        x.append(date_dict)
    return jsonify(x)

@app.route('/api/v1.0/stations')
def stations():

    station_tuple = session.query(station.station).all()

    session.close()

    station_list = list(np.ravel(station_tuple))

    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def most_active():

    latest_date = dt.date(2017,8,23)

    year_ago =  latest_date - dt.timedelta(days = 365)

    last_12 = session.query(measurement.date, measurement.tobs).filter_by(station = "USC00519281").\
    filter(measurement.date >= year_ago).all()

    session.close()

    last_12_list = []
    for date, tobs in last_12:
        tobs_dict = {}
        tobs_dict[date] = tobs
        last_12_list.append(tobs_dict) 
    return jsonify(last_12_list)     

@app.route('/api/v1.0/<start>')
def start_date(start):

    sel = [func.min(measurement.tobs),
           func.avg(measurement.tobs),
           func.max(measurement.tobs)
    ]
    
    start_filter = session.query(*sel).filter(measurement.date >= start).all()
    start_list = [
        {"TMIN": start_filter[0][0]},
        {"TAVG": start_filter[0][1]},
        {"TMAX": start_filter[0][2]}
    ]
    if start <= '2017-08-23':
        return jsonify(start_list)
    else:
        return jsonify("Error: start date past time horizon, please enter a date before 2017-08-23'")




    session.close()

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):

    sel = [func.min(measurement.tobs),
           func.avg(measurement.tobs),
           func.max(measurement.tobs)
    ]
    
    start_end_filter = session.query(*sel).\
        filter(measurement.date.between(start,end)).all()
    start_end_list = [
        {"TMIN": start_end_filter[0][0]},
        {"TAVG": start_end_filter[0][1]},
        {"TMAX": start_end_filter[0][2]}
    ]
    if (start <= '2017-08-23') and (end >='2010-01-01') :
        return jsonify(start_end_list)
    else:
        return jsonify("Error: start and end date not within time horzion, please enter a start and end date between 2010-01-01 : 2017-08-23")
    


    session.close()
