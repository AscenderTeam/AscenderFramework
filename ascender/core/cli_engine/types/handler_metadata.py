from argparse import ArgumentParser, _SubParsersAction
from typing import Any, Mapping

import rich_argparse

from ascender.core.cli_engine.types.parameter import ParameterInfo
from ascender.core.cli_engine.utils.argparser import RichArgumentParser


class HandlerMetadataInfo_:
    names: list[str]
    description: str | None
    parameters: Mapping[str, ParameterInfo]
    additional: Mapping[str, Any]
    docstring: str | None
    _functionname: str

    def __init__(
        self,
        _functionname: str,
        names: list[str],
        description: str | None = None,
        parameters: Mapping[str, ParameterInfo] | None = None,
        additional: Mapping[str, Any] | None = None,
        docstring: str | None = None
    ) -> None:
        self._functionname = _functionname
        self.names = names
        self.description = description
        self.parameters = parameters or {}
        self.additional = additional or {}
        self.docstring = docstring

    def to_subparser(self, parser: _SubParsersAction) -> ArgumentParser:
        subparser = parser.add_parser(self.names[0], description=self.description, formatter_class=rich_argparse.RichHelpFormatter, aliases=self.names[1:], **self.additional)
        
        subparser.__class__ = RichArgumentParser
        
        for name, param in self.parameters.items():
            param.add_to_parser(name, subparser, doc_string=self.docstring)
        
        return subparser