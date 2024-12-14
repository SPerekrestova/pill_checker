import pytest
from MedsRecognition.meds_recognition import MedsRecognition


@pytest.fixture
def meds_recognition_instance():
    return MedsRecognition()


def test_fetch_active_ingredients_from_api_real_call(meds_recognition_instance):
    # Act
    result = MedsRecognition.fetch_active_ingredients_from_api()

    # Assert
    assert isinstance(result, list), "The result should be a list."
    assert len(result) > 0, "The API should return at least one active ingredient."
    for ingredient in result:
        assert isinstance(ingredient, str), "Each active ingredient should be a string."
