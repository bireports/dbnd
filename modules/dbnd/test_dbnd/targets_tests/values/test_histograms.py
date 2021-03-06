from __future__ import print_function

import logging

import pandas as pd

from targets.values.pandas_values import DataFrameValueType


logger = logging.getLogger(__name__)


class TestHistograms:
    def test_boolean_histogram(self):
        d = {"boolean_column": [True] * 10 + [None] * 10 + [False] * 20 + [True] * 20}
        df = pd.DataFrame(d)
        stats, histograms = DataFrameValueType.get_histograms(df)

        histogram = histograms["boolean_column"]
        assert histogram[0] == [30, 20]
        assert histogram[1] == [True, False]

        stats = stats["boolean_column"]
        assert stats["count"] == 50
        assert stats["non-null"] == 50
        assert stats["null-count"] == 10
        assert stats["distinct"] == 3

    def test_numerical_histogram(self):
        d = {"numerical_column": [1, 3, 3, 1, 5, 1, 5, 5]}
        df = pd.DataFrame(d)
        stats, histograms = DataFrameValueType.get_histograms(df)

        stats = stats["numerical_column"]
        assert stats["count"] == 8
        assert stats["non-null"] == 8
        assert stats["distinct"] == 3
        assert stats["min"] == 1
        assert stats["max"] == 5

    def test_strings_histogram(self):
        d = {
            "string_column": ["Hello World!"] * 10
            + [None] * 10
            + ["Ola Mundo!"] * 15
            + ["Shalom Olam!"] * 20
            + ["Ola Mundo!"] * 15
        }
        df = pd.DataFrame(d)
        stats, histograms = DataFrameValueType.get_histograms(df)

        histogram = histograms["string_column"]
        assert histogram[0] == [30, 20, 10]
        assert histogram[1] == ["Ola Mundo!", "Shalom Olam!", "Hello World!"]

        stats = stats["string_column"]
        assert stats["count"] == 60
        assert stats["non-null"] == 60
        assert stats["null-count"] == 10
        assert stats["distinct"] == 4

    def test_histogram_others(self):
        values = []
        for i in range(1, 101):
            str = "str-{}".format(i)
            new_values = [str] * i
            values.extend(new_values)

        d = dict(string_column=values)
        df = pd.DataFrame(d)
        stats, histograms = DataFrameValueType.get_histograms(df)

        histogram = histograms["string_column"]
        assert len(histogram[0]) == 50 and len(histogram[1]) == 50
        assert histogram[0][0] == 100 and histogram[1][0] == "str-100"
        assert histogram[0][10] == 90 and histogram[1][10] == "str-90"
        assert histogram[0][-2] == 52 and histogram[1][-2] == "str-52"
        assert histogram[0][-1] == sum(range(1, 52)) and histogram[1][-1] == "_others"

        stats = stats["string_column"]
        assert stats["count"] == 5050 == sum(histogram[0])
        assert stats["non-null"] == 5050
        assert stats["null-count"] == 0
        assert stats["distinct"] == 100
