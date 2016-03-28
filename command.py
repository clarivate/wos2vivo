#! /usr/bin/env python
"""
Command line tool for searching the WoS for publications and mapping
to VIVO.

$ wos2vivo "University of Idaho"

"""

import click
from rdflib import Graph

from wos2vivo.harvest import get_publications_for_org
from wos2vivo.utils import output_graph


def console(msg):
    click.echo(msg, err=True)


def valid_span(begin, end):
    if (begin is None) and (end is None):
        return None
    if ((begin is not None) and (end is None)) or\
            ((end is not None) and (begin is None)):
        raise click.BadParameter('If using date range, begin and end must be specified.')
    return dict(begin=begin, end=end)


def get_triples(org, out_file, weeks=1, span=None, format="turtle"):
    g = Graph()
    if span is not None:
        records = get_publications_for_org(org, span=span)
    else:
        records = get_publications_for_org(org, weeks=int(weeks))
    num = 0
    for num, rec in enumerate(records):
        g += rec.to_rdf()

    trips = len(g)
    console("{} records found for query. {} triples created.".format(num or 0, trips))
    if trips > 0:
        if file is not None:
            output_graph(g, destination=out_file, format=format)
        else:
            print output_graph(g, format=format)


@click.command(help="Pass in the organization enhanced name from the Web of Science")
@click.argument('organization')
@click.option('--weeks', default="1", type=click.Choice(["1", "2", "4"]), help='Number of previous weeks to search Web of Science.')
@click.option('--begin', default=None, help="Start date for time span search, e.g. 2016-03-15")
@click.option('--end', default=None, help="End date for time span search, e.g. 2016-03-17")
@click.option('--file', default=None, help="File to save triples to.")
@click.option('--format', default="turtle", type=click.Choice(["nt", "turtle", "n3"]), help="RDFLib serialization format")
def get(organization, weeks, begin, end, file, format):
    out_file = file

    console('Querying for %s.' % organization)

    # Is this a date span query?
    vspan = valid_span(begin, end)
    if vspan is not None:
        console("Querying with start date {} and end date {}.".format(vspan['begin'], vspan['end']))
        get_triples(organization, out_file, span=vspan, format=format)
    else:
        console("Querying for {} weeks.".format(weeks))
        get_triples(organization, out_file, weeks=weeks, format=format)

if __name__ == '__main__':
    get()