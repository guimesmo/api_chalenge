from models import Location, User
from sqlalchemy import or_

from app import db, app


def send_user_notification(user_id):
    notification_text = "Não esqueça de levar seu guarda-chuvas!"
    print("sending notification to %s: %s" % (user_id, notification_text))


def load_forecasts():
    with app.app_context():
        for location in Location.query.all():
            location.load_forecasts()
            db.session.add(location)
            db.session.commit()


def notify_users():
    with app.app_context():
        locations = db.session.query(Location).filter(
            or_(Location.todays_forecast == "rain",
                Location.next_day_forecast == "rain"))

        locations = {
            l.id: l for l in locations
        }

        user_list = db.session.query(User).filter(User.home_location_id.in_(locations.keys()))

        for user in user_list:
            notification_required = False
            if user.next_day_forecast_required():
                notification_required = True  # if next day is required any result is valid
            elif user.home_location_id in locations.keys() and locations[user.home_location_id].todays_forecast == 'rain':
                notification_required = True
            elif user.work_location_id in locations.keys() and locations[user.work_location_id].todays_forecast == 'rain':
                notification_required = True

            # send notification if required
            if notification_required:
                send_user_notification(user.id)

