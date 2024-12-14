import pytest
from MedsRecognition.meds_recognition import MedsRecognition
import os


@pytest.fixture
def meds_recognition_instance():
    return MedsRecognition()

@pytest.fixture(autouse=True)
def cleanup_files():
    yield
    if os.path.exists("active_ingredients.json"):
        os.remove("active_ingredients.json")


def test_fetch_active_ingredients_from_file(meds_recognition_instance, mocker):
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data='["Paracetamol", "Ibuprofen"]'))
    result = MedsRecognition.fetch_active_ingredients()

    assert isinstance(result, list), "Result should be a list."
    assert "Paracetamol" in result, "'Paracetamol' should be in the list."
    assert "Ibuprofen" in result, "'Ibuprofen' should be in the list."


def test_fetch_active_ingredients_empty_file(meds_recognition_instance, mocker):
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data=''))
    mock_fetch_api = mocker.patch("MedsRecognition.meds_recognition.MedsRecognition.fetch_active_ingredients_from_api",
                                  return_value=["Paracetamol"])

    result = MedsRecognition.fetch_active_ingredients()

    mock_fetch_api.assert_called_once()
    assert isinstance(result, list), "Result should be a list."
    assert "Paracetamol" in result, "'Paracetamol' should be in the list."


def test_fetch_active_ingredients_no_file(meds_recognition_instance, mocker):
    mocker.patch("os.path.exists", return_value=False)
    mock_fetch_api = mocker.patch("MedsRecognition.meds_recognition.MedsRecognition.fetch_active_ingredients_from_api",
                                  return_value=["Ibuprofen"])

    result = MedsRecognition.fetch_active_ingredients()

    mock_fetch_api.assert_called_once()
    assert isinstance(result, list), "Result should be a list."
    assert "Ibuprofen" in result, "'Ibuprofen' should be in the list."


def test_fetch_active_ingredients_from_api_mock(meds_recognition_instance, mocker):
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {
        "drugMemberGroup": {
            "drugMember": [
                {"minConcept": {"name": "Acetaminophen"}},
                {"minConcept": {"name": "Amoxicillin"}}
            ]
        }
    }
    mocker.patch("requests.get", return_value=mock_response)

    result = MedsRecognition.fetch_active_ingredients_from_api()

    assert isinstance(result, list), "Result should be a list."
    assert "Acetaminophen" in result, "'Acetaminophen' should be in the list."
    assert "Amoxicillin" in result, "'Amoxicillin' should be in the list."
    assert len(result) == 2, "API should return exactly 2 active ingredients."


def test_find_active_ingredients(meds_recognition_instance, mocker):
    mocker.patch.object(meds_recognition_instance, 'active_ingredients', ["Paracetamol", "Ibuprofen"])
    text = "The patient took Paracetamol and Ibuprofen for the headache."

    result = meds_recognition_instance.find_active_ingredients(text)

    assert isinstance(result, list), "Result should be a list."
    assert "Paracetamol" in result, "'Paracetamol' should be in the result."
    assert "Ibuprofen" in result, "'Ibuprofen' should be in the result."
    assert len(result) == 2, "Result should contain exactly 2 active ingredients."


def test_find_active_ingredients_no_match(meds_recognition_instance, mocker):
    mocker.patch.object(meds_recognition_instance, 'active_ingredients', ["Paracetamol", "Ibuprofen"])
    text = "No active ingredients in this text."

    result = meds_recognition_instance.find_active_ingredients(text)

    assert isinstance(result, list), "Result should be a list."
    assert len(result) == 0, "Result should be empty as there are no matches."


def test_find_active_ingredients_empty_list(meds_recognition_instance, mocker):
    mocker.patch.object(meds_recognition_instance, 'active_ingredients', [])

    with pytest.raises(ValueError, match="Active ingredients list is not loaded."):
        meds_recognition_instance.find_active_ingredients("Paracetamol")


def test_is_valid_ingredient(meds_recognition_instance):
    assert meds_recognition_instance._is_valid_ingredient("Paracetamol"), "Valid ingredient should return True."
    assert not meds_recognition_instance._is_valid_ingredient(""), "Empty string should return False."
    assert not meds_recognition_instance._is_valid_ingredient(None), "None should return False."
    assert not meds_recognition_instance._is_valid_ingredient(123), "Non-string value should return False."
