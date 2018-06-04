import json
import datetime

from geolocation import LocationError
from models import User, get_location, db


class SerializerError(Exception):
    pass


class ValidationError(Exception):
    pass


class ImplementationError(Exception):
    pass


class BaseSerializer:
    input_fields = None
    output_fields = None
    required_fields = None
    validated_data = None

    def __init__(self, instance=None, data=None):
        self._implementation_check()
        self.instance = instance
        if data:
            for attr in data.keys():
                if attr in self.input_fields:
                    setattr(self, attr, data[attr])

    def _implementation_check(self):
        field_types = (
            ('input_fields', list),
            ('output_fields', list),
            ('required_fields', list)
        )
        for field_name, field_type in field_types:
            if not isinstance(getattr(self, field_name), field_type):
                raise ImplementationError("%s must be a %s not %s" % (field_name, field_type,
                                                                      type(getattr(self, field_name))))

    def as_dict(self):
        if not self.instance:
            raise SerializerError("No serializable instance")
        output = {}

        for field in self.output_fields:
            output_method = getattr(self, "get_" + field, None)
            if output_method:
                output[field] = output_method()
            else:
                output[field] = getattr(self.instance, field)
        return output

    def serialize(self):
        return json.dumps(self.as_dict())

    def create(self):
        raise NotImplementedError

    def _validate_required_fields(self, data):
        for field in self.required_fields:
            if not data.get(field):
                raise ValidationError("Missing required field %s" % field)

    def _validate_fields(self, data):
        for field in self.input_fields:
            value = data.get(field)
            try:
                field_validation = getattr(self, "validate_" + field)
            except AttributeError:
                self.validated_data[field] = value
            else:
                self.validated_data[field] = field_validation(value)
        return self.validated_data

    def validate(self, data):
        """
        Validates data running field validation and multiple itens check
        :param data: Dict with hard data
        :return: Dict cleaned data
        """
        self._validate_required_fields(data)
        self.validated_data = {}
        return self._validate_fields(data)


class UserSerializer(BaseSerializer):
    model = User
    validated_data = None

    input_fields = [
        'username', 'name',
        'monitor_start_hour', 'monitor_finish_hour',
        'home_city_name', 'home_city_uf',
        'work_city_name', 'work_city_uf'
    ]

    required_fields = [
        'username', 'name', 'home_city_name', 'home_city_uf'
    ]

    output_fields = [
        'username', 'name', 'monitor_start_hour', 'monitor_finish_hour',
        'home_location_name', 'work_location_name'
    ]

    def create(self):
        if not self.validated_data:
            raise SerializerError("You must run the 'validate' method before create")
        instance = User(username=self.validated_data['username'],
                        name=self.validated_data['name'],
                        monitor_start_hour=self.validated_data.get('monitor_start_hour'),
                        monitor_finish_hour=self.validated_data.get('monitor_finish_hour'),
                        home_location_id=self.validated_data['home_location_id'],
                        work_location_id=self.validated_data.get('work_location_id')
                        )
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self):
        if not self.validated_data:
            raise SerializerError("You must run the 'validate' method before update")

        self.instance.username = self.validated_data['username']
        self.instance.name = self.validated_data['name']
        self.instance.monitor_start_hour = self.validated_data.get('monitor_start_hour')
        self.instance.work_leaving_hour = self.validated_data.get('work_leaving_hour')
        self.instance.home_location_id = self.validated_data['home_location_id']
        self.instance.work_location_id = self.validated_data.get('work_location_id')
        db.session.commit()
        return self.instance

    def validate(self, data):
        self.validated_data = super().validate(data)
        try:
            self.validated_data['home_location_id'] = self.validate_home_location(data)
            self.validated_data['work_location_id'] = self.validate_work_location(data)
        except ValidationError as e:
            self.validated_data = None
            raise e
        return self.validated_data

    def validate_username(self, value):
        if self.instance:
            if self.instance.username == value:
                return value
        if db.session.query(User).filter_by(username=value).count():
            raise ValidationError("Username already registered")
        return value

    def generic_validate_hour(self, value):
        if value is None or value == "":
            return
        try:
            datetime.time(*([int(v) for v in value.split(":")]))
        except (ValueError, TypeError):
            raise ValidationError("Invalid hour %s" % value)

        return value

    def validate_monitor_start_hour(self, value):
        return self.generic_validate_hour(value)

    def validate_monitor_finish_hour(self, value):
        return self.generic_validate_hour(value)

    def validate_home_location(self, data):
        try:
            home_location = get_location(data['home_city_name'],
                                         data['home_city_uf'])
        except KeyError:
            raise ValidationError("Home city and uf are required for user registration")
        except LocationError:
            raise ValidationError("Could not find the geolocation for the home address")

        return home_location.id

    def validate_work_location(self, data):
        if not data.get('work_city_name') or not data.get('work_city_uf'):
            return  # no action required
        try:
            work_location = get_location(data['work_city_name'],
                                         data['work_city_uf'])
        except LocationError:
            raise SerializerError("Could not find the geolocation for the work address")

        return work_location.id

    def get_home_location_name(self):
        return "%s, %s" % (self.instance.home_location.city_name, self.instance.home_location.uf)

    def get_work_location_name(self):
        if self.instance.work_location:
            return "%s, %s" % (self.instance.work_location.city_name, self.instance.work_location.uf)