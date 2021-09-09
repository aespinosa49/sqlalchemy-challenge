#imports 
import numpy as np
import datetime as dt
from numpy.core.defchararray import find

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func

# import Flask
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

#Base.classes.keys()
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


#list all routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Rainfall Results: /api/v1.0/precipitation<br/>"
        f"Station List: /api/v1.0/stations<br/>"
        f"Most Active Station: /api/v1.0/tobs<br/>"
        f"Add Start Date (YEAR-MONTH-DATE): /api/v1.0/<start><br/>"
        f"Add Start And End Date (YEAR-MONTH-DATE: /api/v1.0/<start>/<end><br/>")

#Convert the query results to a dictionary using date as the key and prcp as the value
#Return the JSON representation of your dictionary

@app.route("/api/v1.0/precipitation")
def rainfall():
    prioryear = dt.date(2017, 8, 23) - dt.timedelta(days =365)
    rainfall = session.query(Measurement.date, Measurement.prcp).\
             filter(Measurement.date > prioryear).\
             order_by(Measurement.date).all()
    session.close()         

    rainfall_data = []
    for i in rainfall:
        data ={}
        data['date'] = rainfall[0]
        data['prcp'] = rainfall[1]
        rainfall_data.append(data)
    return jsonify(rainfall_data)

#Return a JSON list of stations from the dataset

@app.route("/api/v1.0/stations")
def stations():
    Stations = session.query(Station.station).all()
    session.close()
    all_stations = list(np.ravel(Stations))
    return jsonify(all_stations)

#Query the dates and temperature observations of the most active station for the last year of data
#Return a JSON list of temperature observations (TOBS) for the previous year

@app.route("/api/v1.0/tobs")
def tobs():
    Activity = (session.query(Measurement.station, func.count(Measurement.station)).\
                group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all())
    Most_Active = Activity[0][0]
    prioryear = dt.date(2017, 8, 23) - dt.timedelta(days =365)
    TOBS_Filter = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
                filter(Measurement.station == Most_Active).\
                filter(Measurement.date > prioryear).order_by(Measurement.date).all()
    session.close()            

    MOST_TOBS = []
    for i in TOBS_Filter:
        Active = {}
        Active['date'] = TOBS_Filter[0]
        Active['tobs'] = TOBS_Filter[1]
        MOST_TOBS.append(Active)
    return jsonify(MOST_TOBS)

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range

@app.route("/api/v1.0/<start>")
def start_up(start):
    start_results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >=start)
    session.close() 

    Start_Temp_Data = []
    for min, max, avg in start_results:
        start_dict = {}
        start_dict['TMIN'] = min
        start_dict['TMAX'] = max
        start_dict['TAVG'] = avg
        Start_Temp_Data.append(start_dict)
    return jsonify(Start_Temp_Data)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    start_end_results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >=start).filter(Measurement.date <= end)
    session.close() 

    Start_end_Temp_Data = []
    for min, max, avg in start_end_results:
        start_end_dict = {}
        start_end_dict['TMIN'] = min
        start_end_dict['TMAX'] = max
        start_end_dict['TAVG'] = avg
        Start_end_Temp_Data.append(start_end_dict)
    return jsonify(Start_end_Temp_Data)





if __name__ == '__main__':
    app.run(debug=True)

