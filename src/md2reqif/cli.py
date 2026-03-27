"""Command-line interface for md2reqif."""
from __future__ import annotations
import sys
from pathlib import Path
import click
from md2reqif import __version__
from md2reqif.md_parser import parse as md_parse
from md2reqif.reqif_writer import write as reqif_write
from md2reqif.reqif_reader import read as reqif_read
from md2reqif.md_writer import write as md_write


@click.group()
@click.version_option(__version__)
def main() -> None:
    """md2reqif — Convert Markdown requirements to ReqIF and back."""


@main.command()
@click.argument("input", type=click.Path(exists=True, dir_okay=False))
@click.option("-o", "--output", default=None, help="Output .reqif file (default: stdout)")
@click.option("--pretty/--no-pretty", default=True, show_default=True)
def convert(input: str, output: str | None, pretty: bool) -> None:
    """Convert Markdown requirements to ReqIF XML."""
    text = Path(input).read_text(encoding="utf-8")
    doc = md_parse(text)
    result = reqif_write(doc, pretty=pretty)
    if output:
        Path(output).write_text(result, encoding="utf-8")
        click.echo(f"Written to {output}", err=True)
    else:
        click.echo(result)


@main.command()
@click.argument("input", type=click.Path(exists=True, dir_okay=False))
@click.option("-o", "--output", default=None, help="Output .md file (default: stdout)")
def reverse(input: str, output: str | None) -> None:
    """Convert ReqIF XML back to Markdown."""
    text = Path(input).read_text(encoding="utf-8")
    doc = reqif_read(text)
    result = md_write(doc)
    if output:
        Path(output).write_text(result, encoding="utf-8")
        click.echo(f"Written to {output}", err=True)
    else:
        click.echo(result)


@main.command()
@click.argument("input", type=click.Path(exists=True, dir_okay=False))
def validate(input: str) -> None:
    """Validate a ReqIF file (XML well-formedness)."""
    from xml.etree import ElementTree as ET
    try:
        ET.parse(input)
        click.echo(f"✓ {input} is well-formed XML")
    except ET.ParseError as e:
        click.echo(f"✗ XML parse error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=5000, type=int, help="Port to listen on")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def serve(host: str, port: int, debug: bool) -> None:
    """Start the web interface."""
    from md2reqif.web import app
    click.echo(f"Starting md2reqif web interface at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
