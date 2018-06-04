import pytest
from serializers import UserSerializer, ValidationError


def test_generic_validate_hour():
    serializer = UserSerializer()
    assert serializer.generic_validate_hour("10:00") == "10:00"


def test_generic_validate_hour_raises_on_error():
    serializer = UserSerializer()
    with pytest.raises(ValidationError) as execinfo:
        serializer.generic_validate_hour("25:00")
    assert "Invalid hour" in str(execinfo.value)
