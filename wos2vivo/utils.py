
from record import (
    D,
    BIBO,
    OBO,
    VCARD,
    VIVO
)


def output_graph(graph, destination=None, format="turtle"):
    """
    Helper to output graph with namespaces bound.
    """
    graph.bind("d", D)
    graph.bind("vivo", VIVO)
    graph.bind("vcard", VCARD)
    graph.bind("obo", OBO)
    graph.bind("bibo", BIBO)
    return graph.serialize(destination=destination, format=format)