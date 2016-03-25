"""
Build query documents for the WoS Lite API.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom

ns = {
    "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
    "woksearchlite": "http://woksearchlite.v3.wokmws.thomsonreuters.com",
}

ET.register_namespace("soapenv", ns["soapenv"])
ET.register_namespace("woksearchlite", ns["woksearchlite"])


# Base SOAP message for querying.
QUERY = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
   xmlns:woksearchlite="http://woksearchlite.v3.wokmws.thomsonreuters.com">
   <soapenv:Header/>
   <soapenv:Body>
      <woksearchlite:search>
         <queryParameters>
         </queryParameters>
         <retrieveParameters>
         </retrieveParameters>
      </woksearchlite:search>
   </soapenv:Body>
</soapenv:Envelope>
"""


class Query(object):
    """
    Build query messages.

    """
    def __init__(self, query, weeks=None, span=None, start=1, count=100):
        if query is None:
            raise Exception("No query passed. Query required.")
        self.root = ET.fromstring(QUERY)
        search = self.root.find(".//queryParameters")
        qp = self.query_params(query)
        search.extend(qp)
        date_params = self.date(weeks, span)
        if date_params is not None:
            # Append date
            search.append(date_params)
        # Query Language required.
        search.append(self._elem("queryLanguage", "en"))
        retrieve = self.root.find(".//retrieveParameters")
        rp = self.retrieve_params(start, count)
        retrieve.extend(rp)

    @staticmethod
    def _elem(name, text=None):
        e = ET.Element(name)
        if text is not None:
            e.text = text
        return e

    def query_params(self, query):
        qp = self._elem("queryParameters")
        db = self._elem("databaseId", text="WOS")
        uq = self._elem("userQuery", text=query)
        qp.append(db)
        qp.append(uq)
        return qp

    def retrieve_params(self, first, count):
        rp = self._elem("retrieveParameters")
        first = self._elem("firstRecord", str(first))
        rp.append(first)
        count = self._elem("count", str(count))
        rp.append(count)
        return rp

    def date(self, weeks, span):
        if weeks is not None:
            if weeks not in [1, 2, 4]:
                raise Exception("Valid week parameters are 1, 2, 4")
            wk_str = "{}week".format(weeks)
            symbolic_time = self._elem("symbolicTimeSpan", wk_str)
            return symbolic_time
        elif span is not None:
            if (span.get('start')) or (span.get('end') is None):
                Exception("Both start and end are required for time span queries.")
            ts = ET.Element('timeSpan')
            begin = ET.Element('begin')
            begin.text = span['start']
            end = ET.Element('end')
            end.text = span['end']
            ts.append(begin)
            ts.append(end)
            return ts
        else:
            return

    def to_string(self):
        return ET.tostring(self.root)

    def pretty(self):
        xstring = ET.tostring(self.root)
        xml = minidom.parseString(xstring)
        return xml.toprettyxml(indent=u" ")

# SOAP message for retrieving prior query
RETRIEVE = """
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
  <ns2:retrieve xmlns:ns2="http://woksearchlite.v3.wokmws.thomsonreuters.com">

    <queryId>1</queryId>

    <retrieveParameters>
       <firstRecord>101</firstRecord>
       <count>100</count>
    </retrieveParameters>

  </ns2:retrieve>
</soap:Body>
</soap:Envelope>
"""


class Retrieve(object):

    """
    Retrieve query builder. See:
    http://ipscience-help.thomsonreuters.com/wosWebServicesLite/WebServiceOperationsGroup/WebServiceOperations/g2/retrieve.html
    """

    def __init__(self, qid, start=1, count=100):
        if qid is None:
            raise Exception("No query id passed. Query id required.")
        self.root = ET.fromstring(RETRIEVE)

        query_id = self.root.find(".//queryId")
        query_id.text = qid

        first = self.root.find(".//firstRecord")
        first.text = str(start)

        num = self.root.find(".//count")
        num.text = str(count)

    def to_string(self):
        return ET.tostring(self.root)


if __name__ == "__main__":
    wq = Query("DO=10.1016/S0165-1765(99)00249-9")
    print wq.to_string()