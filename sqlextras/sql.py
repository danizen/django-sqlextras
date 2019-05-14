import logging
from pathlib import Path

import attr
import sqlparse
from sqlparse.tokens import Token as TokenType
from sqlparse.sql import Function, Token, Identifier

log = logging.getLogger(__name__)


class DDLType(object):
    VIEW = 'VIEW'
    TRIGGER = 'TRIGGER'
    PROCEDURE = 'PROCEDURE'
    FUNCTION = 'FUNCTION'
    INDEX = 'INDEX'
    TABLE = 'TABLE'
    SEQUENCE = 'SEQUENCE'
    PACKAGE = 'PACKAGE'
    SYNONYM = 'SYNONYM'

    @classmethod
    def values(cls):
        if not hasattr(cls, '__types'):
            cls.__values = [v for k, v in cls.__dict__.items()
                            if not k.startswith('_') and isinstance(v, str) and k == v]
        return cls.__values


@attr.s(frozen=True)
class DDLObject(object):
    otype = attr.ib(type=str, converter=lambda v: str(v).upper())
    name = attr.ib(type=str, converter=lambda v: str(v).upper())


@attr.s(frozen=True)
class DDLAction(object):
    action = attr.ib(type=str, converter=lambda v: str(v).upper())
    object = attr.ib(type=DDLObject)


def parse_tokens_from_stream(stream, encoding='utf-8'):
    statements = sqlparse.parse(stream, encoding=encoding)
    return [token for statement in statements for token in statement.tokens]


def parse_tokens_from_file(pathlike, encoding='utf-8'):
    path = Path(str(pathlike))
    with path.open(encoding=encoding) as fp:
        tokens = parse_tokens_from_stream(fp, encoding=encoding)
    return tokens


def ddl_indices(tokens):
    return [i for i, token in enumerate(tokens) if token.ttype == TokenType.Keyword.DDL]


def next_ddl_keyword(tokens):
    tokeniter = iter(tokens)
    token = next(tokeniter)
    while not (isinstance(token, Token)
               and token.ttype == TokenType.Keyword.DDL):
        token = next(tokeniter)
    return token


def next_type_keyword(tokens, values):
    tokeniter = iter(tokens)
    token = next(tokeniter)
    while not (isinstance(token, Token)
               and token.ttype == TokenType.Keyword
               and token.value.upper() in values):
        token = next(tokeniter)
    return token


def next_identifier_or_function(tokens):
    tokeniter = iter(tokens)
    token = next(tokeniter)
    while not isinstance(token, (Identifier, Function)):
        token = next(tokeniter)
    return token


def parse_actions_from_file(pathlike, encoding='utf-8'):
    tokens = parse_tokens_from_file(pathlike, encoding=encoding)
    ddl_actions = list()
    indices = ddl_indices(tokens)
    for i in range(len(indices)):
        if i < len(indices) - 1:
            subtokens = tokens[indices[i]:indices[i+1]]
        else:
            subtokens = tokens[indices[i]:]
        try:
            tokeniter = iter(subtokens)
            ddltok = next_ddl_keyword(tokeniter)
            typetok = next_type_keyword(tokeniter, DDLType.values())
            idtok = next_identifier_or_function(tokeniter)
            if isinstance(idtok, Identifier):
                if (typetok.value == DDLType.VIEW
                        and len(idtok.tokens) > 1
                        and idtok.tokens[0].ttype == TokenType.Name):
                    ddl_object = DDLObject(typetok.value, idtok.tokens[0].value)
                else:
                    ddl_object = DDLObject(typetok.value, idtok.value)
            elif isinstance(idtok, Function):
                ddl_object = DDLObject(typetok.value, idtok.tokens[0].value)
            ddl_actions.append(DDLAction(ddltok.value, ddl_object))
        except StopIteration:
            log.error('Reached end of iteration before finding valid keyword/identifier')
            pass
    return ddl_actions


def parse_objects_from_file(pathlike, encoding='utf-8'):
    return set(action.object for action in parse_actions_from_file(pathlike, encoding=encoding))
