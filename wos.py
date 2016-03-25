"""
Login and query WoS Web Services Expanded
"""

import base64
import os
import xml.etree.ElementTree as ET

import logging
logger = logging.getLogger(__name__)

from requests import Session

import constants
from record import Record


class WoSSession(Session):

    def __init__(self, login=True):
        """
        Pass login=False to not authenticate when the session
        is created. This is only used in testing.

        :param login: boolean
        :return: WoSSession
        """
        super(WoSSession, self).__init__()
        self.login = login

    def __enter__(self):
        if self.login is True:
            self.authenticate()
        return self

    def __exit__(self, type, value, tb):
        self.close()

    @staticmethod
    def wauth_header():
        return {"Authorization": "Basic %s" % base64.b64encode("%s:%s" % (os.environ['WOS_USER'], os.environ['WOS_PASSWORD']))}

    def authenticate(self):
        logger.debug("Authenticating with WoS.")
        rsp = self.post(
            constants.AUTH_URL,
            data=constants.AUTHENTICATE,
            headers=self.wauth_header()
        )
        if rsp.status_code == 500:
            raise Exception("WoS returned 500 error:\n" + rsp.text)
        return rsp.status_code

    def query(self, query_doc):
        rsp = self.post(constants.SEARCH_URL, data=query_doc)
        logger.debug("WOS query:\n {}".format(query_doc))
        logger.debug("Query status code: {}".format(rsp.status_code))
        return rsp.text

    def close(self):
        rsp = self.post(constants.AUTH_URL, data=constants.CLOSE)
        logger.debug("Closing session. Status code: {}.".format(rsp.status_code))
        if rsp.status_code != 200:
            logger.error(rsp.text)
            raise Exception("Failed to close WoS session")


class QueryResponse(object):

    def __init__(self, response_text):
        root = ET.fromstring(response_text)
        qrsp = root.find('.//return')
        self.query_id = qrsp.find('queryId').text
        self.found = int(qrsp.find('recordsFound').text)
        self.records = [Record(r) for r in qrsp.findall('records')]
        self.number = len(self.records)

    def has_more(self):
        """
        Determine if query has more records to fetch.
        :return: boolean
        """
        return self.found > self.number
