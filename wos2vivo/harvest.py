import logging
logger = logging.getLogger(__name__)

from client import WoSSession, QueryResponse
from query import Query, Retrieve


def get_publications(query, weeks=None, span=None, batch_size=100):
    """
    Function to get all publications for a given query during a given
    time period.

    :param query: str
    :param weeks: int
    :param span: dict
    :param batch_size: int
    :return: record.Record
    """
    if (weeks is None) and (span is None):
        raise Exception("Invalid query. Weeks or span is required.")
    # Run a query and get all of the records as ntriples.
    with WoSSession() as s:
        q = Query(query, weeks=weeks, span=span).to_string()
        rsp = s.query(q)
        query_response = QueryResponse(rsp)
        for rec in query_response.records:
            yield rec
        logger.info("Found {} records for query {}.".format(query_response.found, query))

        # Page through the results sets to get all the records for given query params.
        queries = 1
        while True:
            start = (batch_size * queries) + 1
            # Break now if we don't have more records to fetch.
            if start >= query_response.found:
                break
            logger.debug("Batch start {}. Batch size {}.".format(start, batch_size))
            # Build retrieve query
            rq = Retrieve(query_response.query_id, start=start, count=batch_size).to_string()
            rsp = s.query(rq)
            # Retrieve response
            retrieve_response = QueryResponse(rsp)
            for rec in retrieve_response.records:
                yield rec
            if retrieve_response.number < batch_size:
                break
            queries += 1
