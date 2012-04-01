# vim:fileencoding=utf8

class ALPError(Exception):
    pass

class ALPLQLExecutionError(ALPError):
    pass

class ALPLQLUnknownExecutionError(ALPLQLExecutionError):
    pass

class ALPLQLParserError(ALPError):
    pass

class ALPLQLUnknownParserError(ALPLQLParserError):
    pass

class ALPApacheError(ALPError):
    pass

class ALPApacheParserError(ALPApacheError):
    pass

class ALPApacheImportError(ALPApacheError):
    pass
