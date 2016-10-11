# Tokenization

## Sentence Tokenization

Use the `sentences` property on a text-based document element to perform sentence segmentation:

    >>> from chemdataextractor.doc import Paragraph
    >>> para = Paragraph('1,4-Dibromoanthracene was prepared from 1,4-diaminoanthraquinone. 1H NMR spectra were recorded on a 300 MHz BRUKER DPX300 spectrometer.')
    >>> para.sentences
    [Sentence('1,4-Dibromoanthracene was prepared from 1,4-diaminoanthraquinone.', 0, 65),
     Sentence('1H NMR spectra were recorded on a 300 MHz BRUKER DPX300 spectrometer.', 66, 135)]

Each sentence object is a document element in itself, and additionally contains the start and end character offsets
within it's parent element.

## Word Tokenization

Use the `tokens` property to get the word tokens:

    >>> para.tokens
    [[Token('1,4-Dibromoanthracene', 0, 21),
      Token('was', 22, 25),
      Token('prepared', 26, 34),
      Token('from', 35, 39),
      Token('1,4-diaminoanthraquinone', 40, 64),
      Token('.', 64, 65)],
     [Token('1H', 66, 68),
      Token('NMR', 69, 72),
      Token('spectra', 73, 80),
      Token('were', 81, 85),
      Token('recorded', 86, 94),
      Token('on', 95, 97),
      Token('a', 98, 99),
      Token('300', 100, 103),
      Token('MHz', 104, 107),
      Token('BRUKER', 108, 114),
      Token('DPX300', 115, 121),
      Token('spectrometer', 122, 134),
      Token('.', 134, 135)]]

This also works on an individual sentence:

    >>> para.sentences[0].tokens
    [Token('1,4-Dibromoanthracene', 0, 21),
     Token('was', 22, 25),
     Token('prepared', 26, 34),
     Token('from', 35, 39),
     Token('1,4-diaminoanthraquinone', 40, 64),
     Token('.', 64, 65)]

There are also `raw_sentences` and `raw_tokens` properties that return strings instead of `Sentence` and
   `Token` objects.

## Using Tokenizers Directly

All tokenizers have a `tokenize` method that takes a text string and returns a list of tokens:

    >>> from chemdataextractor.nlp.tokenize import ChemWordTokenizer
    >>> cwt = ChemWordTokenizer()
    >>> cwt.tokenize('1H NMR spectra were recorded on a 300 MHz BRUKER DPX300 spectrometer.')
    ['1H', 'NMR', 'spectra', 'were', 'recorded', 'on', 'a', '300', 'MHz', 'BRUKER', 'DPX300', 'spectrometer', '.']


There is also a `span_tokenize` method that returns the start and end offsets of the tokens in terms of the
characters in the original string:

    >>> cwt.span_tokenize('1H NMR spectra were recorded on a 300 MHz BRUKER DPX300 spectrometer.')
    [(0, 2), (3, 6), (7, 14), (15, 19), (20, 28), (29, 31), (32, 33), (34, 37), (38, 41), (42, 48), (49, 55), (56, 68), (68, 69)]
