# Chemical Records

ChemDataExtractor processes each document element separately to extract the chemical information, and then merges
data together from every element in the document to produce a single record for each unique chemical entity.

Consider this simple document as an example:

    >>> from chemdataextractor.doc import Document, Heading, Paragraph
    >>> doc = Document(
        Heading('5,10,15,20-Tetra(4-carboxyphenyl)porphyrin (3).'),
        Paragraph('m.p. 90°C.'),
        Paragraph('Melting points were measured in Tetrahydrofuran (THF).'),
    )

Get the records for each element using the `records` property:

    >>> doc[0].records.serialize()
    [{'labels': ['3'], 'names': ['5,10,15,20-Tetra(4-carboxyphenyl)porphyrin']}]
    >>> doc[1].records.serialize()
    [{'melting_points': [{'units': '°C', 'value': '90'}]}]
    >>> doc[2].records.serialize()
    [{'names': ['Tetrahydrofuran', 'THF']}, {'melting_points': [{'solvent': 'Tetrahydrofuran'}]}]

Due to the data interdependencies between the different document elements, each isn't so useful individually. Instead,
it's normally much more useful to get the combined records for the entire document:

    >>> doc.records.serialize()
    [{'names': ['Tetrahydrofuran', 'THF']},
     {'labels': ['3'],
      'names': ['5,10,15,20-Tetra(4-carboxyphenyl)porphyrin']
      'melting_points': [{
        'solvent': 'Tetrahydrofuran',
        'units': '°C',
        'value': '90'
      }],
    }]

ChemDataExtractor has merged the information from all the elements into two unique chemical records.
