import json
import datetime
import time

from flask_sqlalchemy import SQLAlchemy

from geolocation import geolocation_for_address
from weather import Forecast

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)

    monitor_start_hour = db.Column(db.String(5), nullable=True)
    monitor_finish_hour = db.Column(db.String(5), nullable=True)

    alert_time = db.Column(db.Integer, nullable=True)

    home_location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    home_location = db.relationship('Location', backref=db.backref('users_home', lazy=True),
                                                                   foreign_keys=[home_location_id])
    work_location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    work_location = db.relationship('Location', backref=db.backref('users_work', lazy=True),
                                                                   foreign_keys=[work_location_id])

    def __repr__(self):
        return '<User %r>' % self.username

    def __str__(self):
        return self.username

    def next_day_forecast_required(self):
        if self.monitor_start_hour and self.monitor_finish_hour:
            time_tuple = lambda stime: datetime.time(*[int(t) for t in stime.split(":")])
            monitor_start_hour = time_tuple(self.monitor_start_hour)
            monitor_finish_hour = time_tuple(self.monitor_finish_hour)
            return monitor_start_hour > monitor_finish_hour
        return False


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(120), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    lat = db.Column(db.String(20))
    lon = db.Column(db.String(20))

    todays_forecast = db.Column(db.String(120))
    next_day_forecast = db.Column(db.String(120))

    hourly_forecast = db.Column(db.Text())
    last_update = db.Column(db.DateTime, nullable=True)

    def load_lat_lon(self):
        full_address = "%s, %s" % (self.city_name, self.uf)
        lat_lon = geolocation_for_address(full_address)
        self.lat = lat_lon['lat']
        self.lon = lat_lon['lng']

    def load_forecasts(self):
        forecast = Forecast(self.lat, self.lon)
        self.hourly_forecast = json.dumps(forecast.load_hourly_forecast())

    def today_forecasts(self):
        today = datetime.date.today()
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        today_ts = int(time.mktime(today.timetuple()))
        next_day_ts = int(time.mktime(tomorrow.timetuple()))

        hourly_forecast = json.loads(self.hourly_forecast)

        return {int(key): item for key, item in hourly_forecast.items() if (int(key) > today_ts < next_day_ts)}

    def tomorrow_forecasts(self):
        today = datetime.date.today()
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        today_ts = int(time.mktime(today.timetuple()))
        next_day_ts = int(time.mktime(tomorrow.timetuple()))

        hourly_forecast = json.loads(self.hourly_forecast)

        return {int(key): item for key, item in hourly_forecast.items() if (key > next_day_ts)}



def get_location(city, uf):
    location = Location.query.filter_by(city_name=city, uf=uf).first()
    if not location:
        location = Location(city_name=city, uf=uf)
        location.load_lat_lon()
        db.session.add(location)
        db.session.commit()
    return location
