# Chemical Named Entity Recognition


Use the `cems` property on a document or any document element to get a list of the chemical entity mentions:

    >>> doc.cems
    [Span('5,10,15,20-Tetra(4-carboxyphenyl)porphyrin', 19, 61),
     Span('THF', 82, 85),
     Span('Tetrahydrofuran', 65, 80)]

Each mention is returned as a `Span`, which contains the mention text, as well as the start and end character
offsets within the containing document element.
