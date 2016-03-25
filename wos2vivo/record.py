# -*- coding: utf-8 -*-
"""
Read WoS records and map to VIVO.
"""

import os
from rdflib import Namespace, Graph, RDF, Literal, RDFS, XSD
from rdflib.resource import Resource
from time import strptime
from nameparser import HumanName

# Namespaces
D = Namespace(os.environ['DATA_NAMESPACE'])
VIVO = Namespace('http://vivoweb.org/ontology/core#')
BIBO = Namespace('http://purl.org/ontology/bibo/')
OBO = Namespace('http://purl.obolibrary.org/obo/')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')


class Record(object):
    """
    Parse the XML returned by the WoS API.
    Convert to VIVO RDF with to_rdf.
    """

    def __init__(self, element):
        self.root = element

    def ut(self):
        return self.root.find('uid').text

    def title(self):
        return self.root.find("title/value").text

    def authors(self):
        out = []
        for au in self.root.findall('authors/value'):
            out.append(au.text)
        return out

    def _identifier(self, tag):
        for item in self.root.findall('other'):
            if item.find('label').text == "Identifier.{}".format(tag):
                return item.find('value').text

    def doi(self):
        return self._identifier('Doi')

    def _source(self, label):
        for item in self.root.findall('source'):
            if item.find('label').text == label:
                return item.find('value').text

    def venue(self):
        return self._source("SourceTitle")

    def issue(self):
        return self._source("Issue")

    def volume(self):
        return self._source("Volume")

    def pages(self):
        return self._source("Pages")

    def date(self):
        month = None
        year = self._source("Published.BiblioYear")
        raw_month = self._source("Published.BiblioDate")
        if raw_month is not None:
            month = raw_month.split()[0]
        return month, year

    def issn(self):
        return self._identifier("Issn")

    def eissn(self):
        return self._identifier("Eissn")

    def isbn(self):
        return self._identifier("Eisbn")

    """
    VIVO publication from WoS.
    """

    @property
    def localid(self):
        """
        Property used in building URIS.
        """
        return self.ut().replace(':', '-')

    @property
    def pub_uri(self):
        return D['pub-' + self.localid]

    @staticmethod
    def vivo_type():
        """
        For now return all WoS records as AcademicArticles.
        ToDo: add more specific types.
        """
        return BIBO.AcademicArticle

    def in_book(self):
        """
        Determine if item is published in a book.
        :return: boolean
        """
        if self.isbn() is not None:
            return True
        else:
            return False

    def pub_date(self):
        """
        Convert WoS date to year and month.
        """
        month, year = self.date()
        try:
            month_num = strptime(month.split()[0], "%b").tm_mon
        except (ValueError, AttributeError):
            month_num = None
        return year, month, month_num

    def add_date(self):
        """
        Add vivo:DateTimeValue for publication.
        :return: rdflib.Graph
        """
        g = Graph()
        date_uri = D['date-' + self.localid]
        de = Resource(g, date_uri)
        de.set(RDF.type, VIVO.DateTimeValue)
        year, month, month_num = self.pub_date()
        # Add year and month if possible.
        if month_num is not None:
            de.set(RDFS.label, Literal("{}, {}".format(month, year)))
            de.set(
                VIVO.dateTime,
                Literal("{}-{}".format(year, month_num), datatype=XSD.dayMonth)
            )
            de.set(VIVO.dateTimePrecision, VIVO.yearMonthPrecision)
        else:
            de.set(RDFS.label, Literal(year))
            de.set(
                VIVO.dateTime,
                Literal("{}".format(year), datatype=XSD.year)
            )
            de.set(VIVO.dateTimePrecision, VIVO.yearPrecision)

        g.add((self.pub_uri, VIVO.dateTimeValue, date_uri))
        return g

    def add_venue(self):
        """
        Add publication venue.
        :return: rdflib.Graph
        """
        g = Graph()

        if self.in_book() is True:
            vtype = BIBO.Book
            isbn = self.isbn()
            if isbn is None:
                raise Exception("Book can't have null ISBN for {}.".format(self.ut()))
            uri = D['venue-' + isbn]
        else:
            vtype = BIBO.Journal
            issn = self.issn() or self.eissn()
            if issn is None:
                raise Exception("Journal can't have null ISSN for {}.".format(self.ut()))
            uri = D['venue-' + issn]

        venue = Resource(g, uri)
        venue.set(RDF.type, vtype)
        venue.set(RDFS.label, Literal(self.venue))
        if vtype == BIBO.Journal:
            venue.set(BIBO.issn, Literal(issn))
        else:
            venue.set(BIBO.isbn, Literal(isbn))
        g.add((self.pub_uri, VIVO.hasPublicationVenue, uri))

        return g

    def add_vcard(self, position, name):
        """
        :param position: number in author order
        :param name: name as string - last, first, middle
        :return: rdflib.Graph
        """
        g = Graph()

        # vcard individual
        vci_uri = D['vcard-individual-' + position + '-' + self.localid]
        g.add((vci_uri, RDF.type, VCARD.Individual))

        # vcard name
        vcn_uri = D['vcard-name-' + position + '-' + self.localid]
        g.add((vcn_uri, RDF.type, VCARD.Name))
        g.add((vcn_uri, RDFS.label, Literal(name)))
        # Parse name into first, last, middle
        name = HumanName(name)
        g.add((vcn_uri, VCARD.givenName, Literal(name.first)))
        g.add((vcn_uri, VCARD.familyName, Literal(name.last)))
        if name.middle != "":
            g.add((vcn_uri, VIVO.middleName, Literal(name.middle)))
        # Relate vcard individual to vcard name
        g.add((vci_uri, VCARD.hasName, vcn_uri))
        return vci_uri, g

    def authorship(self):
        """
        Add authorship statements and vcards for authors.
        :return: rdflib.Graph
        """
        g = Graph()
        for num, au in enumerate(self.authors()):
            position = str(num + 1)

            vcard_individual_uri, vcard_stmts = self.add_vcard(position, au)
            g += vcard_stmts

            # Authorship
            aship_uri = D['authorship-' + position + '-' + self.localid]
            g.add((aship_uri, RDF.type, VIVO.Authorship))
            g.add((aship_uri, VIVO.rank, Literal(int(position))))

            # Relate pub and authorship
            g.add((aship_uri, VIVO.relates, self.pub_uri))

            # Relate vcard and authorship
            g.add((aship_uri, VIVO.relates, vcard_individual_uri))

        return g

    def add_vcard_weblink(self):
        """
        Build statements for weblinks in VIVO.
        :return: rdflib.Graph
        """
        base_url = "http://ws.isiknowledge.com/cps/openurl/service?url_ver=Z39.88-2004&rft_id=info:ut/WOS:{}"
        g = Graph()

        # vcard individual for pub
        vci_uri = D['vcard-individual-pub-' + self.localid]
        g.add((vci_uri, RDF.type, VCARD.Individual))

        # vcard URL
        vcu_uri = D['vcard-url-pub-' + self.localid]
        g.add((vcu_uri, RDF.type, VCARD.URL))
        g.add((vcu_uri, RDFS.label, Literal(u"Web of Science™")))
        g.add((vcu_uri, VCARD.url, Literal(base_url.format(self.ut()))))

        # Relate vcard individual to url
        g.add((vci_uri, VCARD.hasURL, vcu_uri))
        return vci_uri, g

    def to_rdf(self):
        """
        Convert the API publication object to VIVO RDF.

        :return: rdflib.Graph
        """
        g = Graph()
        pub = Resource(g, self.pub_uri)
        pub.set(RDF.type, self.vivo_type())
        pub.set(RDFS.label, Literal(self.title()))
        # WoS UT. Map to VIVO.identifier for now.
        # ToDo: this should be a more specific property
        pub.set(VIVO.identifier, Literal(self.ut()))
        # DOI
        doi = self.doi()
        if doi is not None:
            pub.set(BIBO.doi, Literal(doi))
        # Volume
        volume = self.volume()
        if volume is not None:
            pub.set(BIBO.volume, Literal(volume))
        # Issue
        issue = self.issue()
        if issue is not None:
            pub.set(BIBO.issue, Literal(issue))
        # Pages
        pages = self.pages()
        if pages is not None:
            start, end = pages.split('-')
            pub.set(BIBO.start, Literal(start))
            pub.set(BIBO.end, Literal(end))

        # publication venue
        g += self.add_venue()
        # date
        g += self.add_date()

        # authorship and vcards
        g += self.authorship()

        # links
        web_link, linkg = self.add_vcard_weblink()
        g += linkg
        # relate web link and publication
        g.add((self.pub_uri, OBO['ARG_2000028'], web_link))

        return g

    def to_nt(self):
        g = self.to_rdf()
        return g.serialize(format='nt')
