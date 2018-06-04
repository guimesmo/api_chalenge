from models import User


def test_if_user_leaves_the_work_in_the_next_day():
    user = User()
    user.monitor_start_hour = "20:00"
    user.monitor_finish_hour = "8:00"
    assert user.next_day_forecast_required() is True


def test_if_user_leaves_the_work_in_the_same_day():
    user = User()
    user.monitor_start_hour = "8:00"
    user.monitor_finish_hour = "20:00"
    assert user.next_day_forecast_required() is False
