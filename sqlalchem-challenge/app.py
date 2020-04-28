import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

   

@app.route("/api/v1.0/precipitation")
def precipitation():
    starting_date = (session.query(Measurement.date)
                     .order_by(Measurement.date.desc())
                     .first())
    starting_date = list(np.ravel(starting_date))[0]
    starting_date = dt.datetime.strptime(starting_date, '%Y-%m-%d')

    s_year = int(dt.datetime.strftime(starting_date, '%Y'))
    s_month = int(dt.datetime.strftime(starting_date, '%m'))
    s_day = int(dt.datetime.strftime(starting_date, '%d'))
    
    ending_date = dt.date(s_year, s_month, s_day) - dt.timedelta(days=365)
    
    prcp_cal = (session.query(Measurement.date, Measurement.prcp)
                  .filter(Measurement.date >= ending_date)
                  .order_by(Measurement.date)
                  .all())
    results_dict = {}
    for result in prcp_cal:
        results_dict[result[0]] = result[1]
    
    
    return(results_dict)

@app.route("/api/v1.0/stations")
def stations():
    station_list = (session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation)
                        .group_by(Station.station)
                        .order_by(Station.id.desc())
                        .all())

    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs(): 
    starting_date = (session.query(Measurement.date)
                     .order_by(Measurement.date.desc())
                     .first())
    starting_date = list(np.ravel(starting_date))[0]
    starting_date = dt.datetime.strptime(starting_date, '%Y-%m-%d')

    s_year = int(dt.datetime.strftime(starting_date, '%Y'))
    s_month = int(dt.datetime.strftime(starting_date, '%m'))
    s_day = int(dt.datetime.strftime(starting_date, '%d'))
    
    ending_date = dt.date(s_year, s_month, s_day) - dt.timedelta(days=365)
    
    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date >= ending_date)
                      .order_by(Measurement.date)
                      .all())

    data = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        tempData.append(tempDict)
    
    return jsonify(data)

@app.route("/api/v1.0/<start>")
def start(start):

    print("Received start date api request.")

    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date = final_date_query[0][0]

    temps = calc_temps(start, max_date)

    return_list = []
    date_dict = {'start_date': start, 'end_date': max_date}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    print("Received start date and end date api request.")

    temps = calc_temps(start, end)

    return_list = []
    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)

if __name__ == "__main__":
    app.run(debug = True)

    
    
    
    

    


