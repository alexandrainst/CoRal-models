"""Unit tests for the `asr.wav2vec2.clean` module."""

import re

import pytest
from datasets import DatasetDict

from coral_models.asr.wav2vec2.clean import clean_transcription


class TestCleanDataset:
    def test_dtype(self, cleaned_dataset) -> None:
        assert isinstance(cleaned_dataset, DatasetDict)

    def test_split_names(self, cleaned_dataset) -> None:
        assert set(cleaned_dataset.keys()) == {"train", "val", "test"}

    def test_train_samples(self, cfg, cleaned_dataset) -> None:
        samples = cleaned_dataset["train"][cfg.dataset.text_column]
        assert samples == [
            "min|fortræffelige|lille|nattergal",
            "jeg|venter|grumme|meget|af|den",
            "men|hendes|vilje|var|fast|som|hendes|tillid|til|vorherre",
            "her|er|kommet|gode|klæder|at|slide|for|de|fire|børn",
            "hver|rose|på|træet|i|haven|havde|sin|historie",
        ]


class TestCleanTranscription:
    transcription = "\nThis is a (test) [sentence]\u0301 with \n{aa} and ğ. "

    empty_punctuation_regex = re.compile(r"")
    parans_punctuation_regex = re.compile(r"[\(\)\[\]\{\}]")
    newline_punctuation_regex = re.compile(r"[\n\r]")

    empty_conversion_dict: dict[str, str] = {}
    diacritics_conversion_dict = {"aa": "å", "ğ": "g"}
    empty_whitespace_conversion_dict = {"\u0301": " "}

    @pytest.mark.parametrize(
        "transcription, punctuation_regex, conversion_dict, expected",
        ids=[
            "empty-empty",
            "empty-diacritics",
            "empty-empty_whitespace",
            "parans-empty",
            "parans-diacritics",
            "parans-empty_whitespace",
            "newline-empty",
            "newline-diacritics",
            "newline-empty_whitespace",
        ],
        argvalues=[
            (
                transcription,
                empty_punctuation_regex,
                empty_conversion_dict,
                "this|is|a|(test)|[sentence]\u0301|with|\n{aa}|and|ğ.",
            ),
            (
                transcription,
                empty_punctuation_regex,
                diacritics_conversion_dict,
                "this|is|a|(test)|[sentence]\u0301|with|\n{å}|and|g.",
            ),
            (
                transcription,
                empty_punctuation_regex,
                empty_whitespace_conversion_dict,
                "this|is|a|(test)|[sentence]|with|\n{aa}|and|ğ.",
            ),
            (
                transcription,
                parans_punctuation_regex,
                empty_conversion_dict,
                "this|is|a|test|sentence\u0301|with|\naa|and|ğ.",
            ),
            (
                transcription,
                parans_punctuation_regex,
                diacritics_conversion_dict,
                "this|is|a|test|sentence\u0301|with|\nå|and|g.",
            ),
            (
                transcription,
                parans_punctuation_regex,
                empty_whitespace_conversion_dict,
                "this|is|a|test|sentence|with|\naa|and|ğ.",
            ),
            (
                transcription,
                newline_punctuation_regex,
                empty_conversion_dict,
                "this|is|a|(test)|[sentence]\u0301|with|{aa}|and|ğ.",
            ),
            (
                transcription,
                newline_punctuation_regex,
                diacritics_conversion_dict,
                "this|is|a|(test)|[sentence]\u0301|with|{å}|and|g.",
            ),
            (
                transcription,
                newline_punctuation_regex,
                empty_whitespace_conversion_dict,
                "this|is|a|(test)|[sentence]|with|{aa}|and|ğ.",
            ),
        ],
    )
    def test_clean_transcription(
        self,
        transcription: str,
        punctuation_regex: re.Pattern[str],
        conversion_dict: dict[str, str],
        expected: str,
    ) -> None:
        cleaned_transcription = clean_transcription(
            doc=transcription,
            punctuation_regex=punctuation_regex,
            conversion_dict=conversion_dict,
        )
        assert cleaned_transcription == expected
