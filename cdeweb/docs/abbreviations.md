# Abbreviation Detection

Abbreviation detection is done using a method based on the algorithm in Schwartz & Hearst 2003.

    >>> p = Paragraph(u'Dye-sensitized solar cells (DSSCs) with ZnTPP = Zinc tetraphenylporphyrin.')
    >>> p.abbreviation_definitions
    [([u'ZnTPP'], [u'Zinc', u'tetraphenylporphyrin'], u'CM'),
     ([u'DSSCs'], [u'Dye', u'-', u'sensitized', u'solar', u'cells'], None)]

Abbreviation definitions are returned as tuples containing the abbreviation, the long name, and an entity tag. The
entity tag is `CM` if the abbreviation is for a chemical entity, otherwise it is `None`.
