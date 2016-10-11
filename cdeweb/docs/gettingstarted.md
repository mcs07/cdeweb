# Getting Started

This page gives a introduction on how to get started with ChemDataExtractor. This assumes you already have
ChemDataExtractor [installed](install).

The simplest way to load a Document into ChemDataExtractor is to pass it some text:

    >>> from chemdataextractor import Document

    >>> doc = Document('UV-vis spectrum of 5,10,15,20-Tetra(4-carboxyphenyl)porphyrin in Tetrahydrofuran (THF).')

Once loaded, it is possible to extract various types of information from this document object.

For example, each individual chemical entity mention (CEM):

    >>> doc.cems
    [Span('5,10,15,20-Tetra(4-carboxyphenyl)porphyrin', 19, 61), Span('THF', 82, 85), Span('Tetrahydrofuran', 65, 80)]

Or abbreviations:

    >>> doc.abbreviation_definitions
    [([u'THF'], [u'Tetrahydrofuran'], u'CM')]


All chemical mentions, abbreviations, properties and spectra are combined to produce a "record" for each unique
chemical entitiy:

    >>> doc.records
    [<Compound>, <Compound>]
    >>> doc.records[0].serialize()
    {'names': ['5,10,15,20-Tetra(4-carboxyphenyl)porphyrin']}
    >>> doc.records[1].serialize()
    {'names': ['Tetrahydrofuran', 'THF']}
