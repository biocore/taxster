import click

import taxster


def print_version(ctx, param, value):
    """Echo package version"""
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version %s' % taxster.__version__)
    ctx.exit()


@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.pass_context
def main(ctx):
    """taxster, canonically pronounced 'tax-ster'"""
    pass
