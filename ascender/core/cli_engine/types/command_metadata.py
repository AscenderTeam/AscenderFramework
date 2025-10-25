from argparse import _SubParsersAction
from collections.abc import Mapping
from typing import Any, Sequence

import rich_argparse

from ascender.core.cli_engine.types.handler_metadata import HandlerMetadataInfo_
from ascender.core.cli_engine.types.parameter import ParameterInfo
from ascender.core.cli_engine.utils.argparser import RichArgumentParser



class BasicMetadata_:
    name: str
    description: str | None
    help: str | None
    kind: str | None
    parameters: Mapping[str, ParameterInfo]
    additional: Mapping[str, Any]

    def __init__(self, name: str, description: str | None, help: str | None, kind: str | None, parameters: Mapping[str, ParameterInfo], additional: Mapping[str, Any]) -> None:
        self.name = name
        self.description = description
        self.help = help
        self.kind = kind
        self.parameters = parameters
        self.additional = additional
    
    def add_to_argparse(self, subparser: _SubParsersAction) -> None:
        """
        Adds the command metadata to the provided ArgumentParser instance.
        """
        command_parser = subparser.add_parser(
            self.name, 
            description=self.description, 
            help=self.help,
            formatter_class=rich_argparse.RichHelpFormatter,
            **self.additional
        )
        command_parser.__class__ = RichArgumentParser
        
        for param_name, param_info in self.parameters.items():
            param_info.add_to_parser(param_name, command_parser)


class GenericMetadata_:
    name: str
    description: str | None
    help: str | None
    kind: str | None
    parameters: Sequence[HandlerMetadataInfo_]
    additional: Mapping[str, Any]

    def __init__(self, name: str, description: str | None, help: str | None, kind: str | None, parameters: Sequence[HandlerMetadataInfo_], additional: Mapping[str, Any]) -> None:
        self.name = name
        self.description = description
        self.help = help
        self.kind = kind
        self.parameters = parameters
        self.additional = additional
    
    def add_to_argparse(self, subparser: _SubParsersAction) -> None:
        """
        Adds the command metadata to the provided ArgumentParser instance.
        """
        command_parser: RichArgumentParser = subparser.add_parser(
            self.name, 
            description=self.description, 
            help=self.help,
            formatter_class=rich_argparse.RichHelpFormatter,
            **self.additional
        )
        command_parser.__class__ = RichArgumentParser
        
        generic_subparsers = command_parser.add_subparsers(
            title=self.name, 
            description=self.description, 
            dest="subcommand", 
            required=False,
            metavar="subcommand"
        )
        for handler in self.parameters:
            handler.to_subparser(generic_subparsers)

