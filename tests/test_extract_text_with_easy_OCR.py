from PIL import Image
from MedsRecognition.ocr_service import extract_text_with_easyocr
import django
import os
import unittest
from unittest.mock import patch, MagicMock

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MedsRecognition.settings")

django.setup()


class TestExtractTextWithEasyOCR(unittest.TestCase):
    @patch("MedsRecognition.ocr_service.easyocr.Reader")
    def test_extract_text_with_easyocr_success(self, mock_reader_class):
        image_mock = MagicMock(spec=Image.Image)
        image_mock.mode = "RGB"

        mock_reader_instance = mock_reader_class.return_value
        mock_reader_instance.readtext.return_value = ["Text1", "Text2"]

        image_mock.save = MagicMock()

        result = extract_text_with_easyocr(image_mock)

        self.assertEqual(result, "Text1 Text2")
        mock_reader_class.assert_called_once_with(["en"], gpu=True)
        mock_reader_instance.readtext.assert_called_once()

    @patch("MedsRecognition.ocr_service.easyocr.Reader")
    def test_extract_text_with_easyocr_no_text(self, mock_reader_class):
        image_mock = MagicMock(spec=Image.Image)
        image_mock.mode = "RGB"

        mock_reader_instance = mock_reader_class.return_value
        mock_reader_instance.readtext.return_value = []

        image_mock.save = MagicMock()

        result = extract_text_with_easyocr(image_mock)

        self.assertEqual(result, "")
        mock_reader_class.assert_called_once_with(["en"], gpu=True)
        mock_reader_instance.readtext.assert_called_once()

    @patch("MedsRecognition.ocr_service.easyocr.Reader")
    def test_extract_text_with_easyocr_image_conversion(self, mock_reader_class):
        image_mock = MagicMock(spec=Image.Image)
        image_mock.mode = "RGBA"

        converted_image_mock = MagicMock(spec=Image.Image)
        image_mock.convert.return_value = converted_image_mock

        mock_reader_instance = mock_reader_class.return_value
        mock_reader_instance.readtext.return_value = ["ConvertedText"]

        result = extract_text_with_easyocr(image_mock)

        self.assertEqual(result, "ConvertedText")
        image_mock.convert.assert_called_once_with("RGB")
        mock_reader_class.assert_called_once_with(["en"], gpu=True)
        mock_reader_instance.readtext.assert_called_once()

    @patch("MedsRecognition.ocr_service.easyocr.Reader")
    def test_extract_text_with_easyocr_error_handling(self, mock_reader_class):
        image_mock = MagicMock(spec=Image.Image)
        image_mock.mode = "RGB"

        mock_reader_instance = mock_reader_class.return_value
        mock_reader_instance.readtext.side_effect = Exception("OCR Error")

        with self.assertRaises(Exception) as context:
            extract_text_with_easyocr(image_mock)

        self.assertEqual(str(context.exception), "OCR Error")
        mock_reader_class.assert_called_once_with(["en"], gpu=True)
        mock_reader_instance.readtext.assert_called_once()


if __name__ == "__main__":
    unittest.main()
