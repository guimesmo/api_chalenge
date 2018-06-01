from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from geolocation import geolocation_for_address
from weather import Forecast

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)

    work_entering_hour = db.Column(db.Integer, nullable=True)
    work_leaving_hour = db.Column(db.Integer, nullable=True)

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
        if self.work_entering_hour and self.work_leaving_hour:
            return self.work_entering_hour > self.work_leaving_hour
        return False


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(120), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    lat = db.Column(db.String(20))
    lon = db.Column(db.String(20))
    todays_forecast = db.Column(db.String(120))
    next_day_forecast = db.Column(db.String(120))
    last_update = db.Column(db.DateTime, nullable=True)

    def load_lat_lon(self):
        full_address = "%s, %s" % (self.city_name, self.uf)
        lat_lon = geolocation_for_address(full_address)
        self.lat = lat_lon['lat']
        self.lon = lat_lon['lng']

    def load_forecasts(self):
        if self.last_update and self.last_update.date() == datetime.utcnow().date():  # no date change
            return
        forecast = Forecast(self.lat, self.lon)
        self.todays_forecast = forecast.todays_forecast
        self.next_day_forecast = forecast.next_day_forecast


def get_location(city, uf):
    location = Location.query.filter_by(city_name=city, uf=uf).first()
    if not location:
        location = Location(city_name=city, uf=uf)
        location.load_lat_lon()
        db.session.add(location)
        db.session.commit()
    return location
