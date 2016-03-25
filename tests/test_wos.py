
import base64
import os
from unittest import TestCase

import betamax
from betamax_serializers import pretty_json
betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)

# Directory where test data is stored.
TEST_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__))
)

# setup recorder
with betamax.Betamax.configure() as config:
    config.define_cassette_placeholder(
    '<base64 encoded WoS username:password>',
    base64.b64encode("%s:%s" % (os.environ['WOS_USER'], os.environ['WOS_PASSWORD']))
    )
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.cassette_library_dir = os.path.join(TEST_PATH, 'fixtures')


from wos2vivo.client import WoSSession, QueryResponse
from wos2vivo.query import Query
from wos2vivo.record import BIBO, OBO, VIVO, VCARD

from rdflib import RDFS, Literal


class TestWos(TestCase):

    def test_org_query(self):
        session = WoSSession(login=False)

        # Setup HTTP session recording
        recorder = betamax.Betamax(session)

        with recorder.use_cassette('query',  record='once'):
            # Login
            session.authenticate()

            # Run query
            query = Query(
                "OG=\"University of Florida\"",
                span=dict(begin="2016-03-15", end="2016-03-15"),
                count=1
            )
            rsp = session.query(query.to_string())

            qrsp = QueryResponse(rsp)
            assert qrsp.found == 3
            assert qrsp.has_more() is True

            # Check a record
            rec = qrsp.records[0]
            # Test returned metadata.
            self.assertEqual(rec.ut(), "WOS:000370312100013")
            self.assertTrue(rec.title().find('Bos taurus cows')> -1)
            self.assertEqual(rec.doi(), "10.1016/j.theriogenology.2015.10.035")

            # Test RDF output
            uri = rec.pub_uri
            g = rec.to_rdf()
            self.assertEqual(
                g.value(subject=uri, predicate=VIVO.identifier),
                Literal("WOS:000370312100013")
            )
            self.assertEqual(
                g.value(subject=uri, predicate=RDFS.label),
                Literal("Select Synch and Co-Synch protocols using a CIDR yield similar pregnancy rates after a fixed-time insemination in suckled Bos indicus x Bos taurus cows")
            )
            self.assertEqual(
                g.value(subject=uri, predicate=BIBO.doi),
                Literal('10.1016/j.theriogenology.2015.10.035')
            )
            # Test number of authorships
            for row in g.query("""
                select (count(?aship) as ?authors)
                where {
                    ?aship vivo:relates ?pub ;
                           vivo:relates ?vcard .
                    ?vcard vcard:hasName ?name .
                }""",
                               initBindings=dict(pub=uri),
                               initNs=(dict(vivo=VIVO, vcard=VCARD))
                               ):
                assert row.authors.toPython() == 5

            # web link
            for row in g.query("""
                select ?url
                where {
                    ?pub obo:ARG_2000028 ?vci .
                    ?vci vcard:hasURL ?vurl .
                    ?vurl vcard:url ?url .
                }""",
                               initBindings=dict(pub=uri),
                               initNs=(dict(obo=OBO, vcard=VCARD))
                               ):
                self.assertEqual(
                    row.url.toPython(),
                    "http://ws.isiknowledge.com/cps/openurl/service?url_ver=Z39.88-2004&rft_id=info:ut/WOS:{}".format(rec.ut())
                )

            session.close()
