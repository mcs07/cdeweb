# Part-of-speech Tagging

ChemDataExtractor contains a chemistry-aware Part-of-speech tagger. Use the `pos_tagged_tokens` property on a
document element to get the tagged tokens:

    >>> s = Sentence('1H NMR spectra were recorded on a 300 MHz BRUKER DPX300 spectrometer.')
    >>> s.pos_tagged_tokens
    [('1H', 'NN'),
     ('NMR', 'NN'),
     ('spectra', 'NNS'),
     ('were', 'VBD'),
     ('recorded', 'VBN'),
     ('on', 'IN'),
     ('a', 'DT'),
     ('300', 'CD'),
     ('MHz', 'NNP'),
     ('BRUKER', 'NNP'),
     ('DPX300', 'NNP'),
     ('spectrometer', 'NN'),
     ('.', '.')]

## Using Taggers Directly

All taggers have a `tag` method that takes a list of token strings and returns a list of (token, tag) tuples:

    >>> from chemdataextractor.nlp.pos import ChemCrfPosTagger
    >>> cpt = ChemCrfPosTagger()
    >>> cpt.tag(['1H', 'NMR', 'spectra', 'were', 'recorded', 'on', 'a', '300', 'MHz', 'BRUKER', 'DPX300', 'spectrometer', '.'])
    [('1H', 'NN'),
     ('NMR', 'NN'),
     ('spectra', 'NNS'),
     ('were', 'VBD'),
     ('recorded', 'VBN'),
     ('on', 'IN'),
     ('a', 'DT'),
     ('300', 'CD'),
     ('MHz', 'NNP'),
     ('BRUKER', 'NNP'),
     ('DPX300', 'NNP'),
     ('spectrometer', 'NN'),
     ('.', '.')]
