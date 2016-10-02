# Lexicon

As ChemDataExtractor processes documents, it adds each unique word that it encounters to the `Lexicon` as a `Lexeme`. 
Each `Lexeme` stores various word features, so they don't have to be re-calculated for every occurrence of that word.

You can access the Lexeme for a token using the `lex` property.

    >>> s = Sentence('Sulphur and Oxygen.')
    >>> s.tokens[0]
    Token('Sulphur', 0, 7)
    >>> s.tokens[0].lex.normalized
    'sulfur'
    >>> s.tokens[0].lex.is_hyphenated
    False
    >>> s.tokens[0].lex.cluster
    '11011101100110'
