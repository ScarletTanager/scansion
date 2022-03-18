import click
import paths
import inspect

def __islatinmeter(obj):
    if inspect.isclass(obj) and obj.__name__ != "BaseMeter":
        return True
    return False

def __getmeters():
    paths.add_repo_paths()
    import meter
    meters = {}
    for name, obj in inspect.getmembers(meter, __islatinmeter):
        meters[name] = obj
    return meters

def list_meters(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    for name in __getmeters().keys():
        click.echo(name)
    ctx.exit()

def get_meter(meter_name):
    paths.add_repo_paths()
    import meter
    meter_class_ = getattr(meter, meter_name)
    return meter_class_()


@click.command()
@click.option('-l', '--list-meters', help='List available meters',
              is_flag=True, is_eager=True, expose_value=False,
              callback=list_meters)
@click.option('-n', '--meter-name', help='Show details for specified meter',
              type=click.Choice(__getmeters().keys(), case_sensitive=False))
def main(meter_name):
    """Get details about available/known meters"""

    click.echo("Meter: {}".format(meter_name))
    click.echo("")
    for p in get_meter(meter_name).patterns():
        click.echo(p)

if __name__ == "__main__":
    exit(main())