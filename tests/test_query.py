from unittest import TestCase

from query import Query, Retrieve

import xml.etree.ElementTree as ET


class TestQuery(TestCase):

    def test_default_query(self):
        uq = "DO=10.1016/S0165-1765(99)00249-9"
        wq = Query(uq)
        tree = ET.fromstring(wq.to_string())
        self.assertEqual(
            tree.find(".//userQuery").text,
            uq
        )

    def test_query_with_retrieve_params(self):
        uq = "peanut allergy"
        wq = Query(uq, start=10, count=10)
        tree = ET.fromstring(wq.to_string())
        self.assertEqual(
            tree.find(".//firstRecord").text,
            "10"
        )
        self.assertEqual(
            tree.find(".//count").text,
            "10"
        )

    def test_query_by_weeks(self):
        wq = Query("peanut allergy", weeks=1).to_string()
        tree = ET.fromstring(wq)
        self.assertEqual(
            tree.find(".//symbolicTimeSpan").text,
            "1week"
        )

    def test_query_by_span(self):
        tspan = {"start": "2015-09-01", "end": "2015-11-31"}
        wq = Query("peanut allergy", span=tspan).to_string()
        tree = ET.fromstring(wq)
        self.assertEqual(
            tree.find(".//timeSpan/begin").text,
            tspan['start']
        )
        self.assertEqual(
            tree.find(".//timeSpan/end").text,
            tspan['end']
        )


class TestRetrieve(TestCase):

    def test_default_query(self):
        wq = Retrieve("1", start=101)
        tree = ET.fromstring(wq.to_string())
        self.assertEqual(
            tree.find(".//queryId").text,
            "1"
        )
        self.assertEqual(
            tree.find(".//firstRecord").text,
            "101"
        )
        self.assertEqual(
            tree.find(".//count").text,
            "100"
        )