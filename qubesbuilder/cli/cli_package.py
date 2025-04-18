import subprocess
from typing import List

import click

from qubesbuilder.cli.cli_base import aliased_group, ContextObj
from qubesbuilder.common import STAGES_ALIAS
from qubesbuilder.component import QubesComponent
from qubesbuilder.config import Config
from qubesbuilder.distribution import QubesDistribution
from qubesbuilder.log import QubesBuilderLogger


@aliased_group("package", chain=True)
def package():
    """
    Package CLI
    """


def _component_stage(
    config: Config,
    components: List[QubesComponent],
    distributions: List[QubesDistribution],
    stages: List[str],
):
    """
    Generic function to trigger stage for a standard component
    """
    QubesBuilderLogger.info(f"Running stages: {', '.join(stages)}")

    for job in config.get_jobs(
        components=components,
        distributions=distributions,
        templates=[],
        stages=stages,
    ):
        job.run()


@click.command(name="all", short_help="Run all package stages.")
@click.pass_obj
def _all_package_stage(obj: ContextObj):
    stages = obj.config.get_stages()
    if obj.config.automatic_upload_on_publish:
        stages.remove("upload")
    # run "fetch" first as other stages may depend on configuration fetched
    # by it
    if "fetch" in stages:
        _component_stage(
            config=obj.config,
            components=obj.components,
            distributions=obj.distributions,
            stages=["fetch"],
        )
        stages.remove("fetch")
    _component_stage(
        config=obj.config,
        components=obj.components,
        distributions=obj.distributions,
        stages=stages,
    )


@package.command()
@click.pass_obj
def fetch(obj: ContextObj):
    _component_stage(
        config=obj.config,
        components=obj.components,
        distributions=obj.distributions,
        stages=["fetch"],
    )


@package.command()
@click.pass_obj
def prep(obj: ContextObj):
    _component_stage(
        config=obj.config,
        components=obj.components,
        distributions=obj.distributions,
        stages=["prep"],
    )


@package.command()
@click.pass_obj
def build(obj: ContextObj):
    _component_stage(
        config=obj.config,
        components=obj.components,
        distributions=obj.distributions,
        stages=["build"],
    )


@package.command()
@click.pass_obj
def post(obj: ContextObj):
    _component_stage(
        config=obj.config,
        components=obj.components,
        distributions=obj.distributions,
        stages=["post"],
    )


@package.command()
@click.pass_obj
def verify(obj: ContextObj):
    _component_stage(
        config=obj.config,
        components=obj.components,
        distributions=obj.distributions,
        stages=["verify"],
    )


@package.command()
@click.pass_obj
def sign(obj: ContextObj):
    _component_stage(
        config=obj.config,
        components=obj.components,
        distributions=obj.distributions,
        stages=["sign"],
    )


@package.command()
@click.pass_obj
def publish(obj: ContextObj):
    _component_stage(
        config=obj.config,
        components=obj.components,
        distributions=obj.distributions,
        stages=["publish"],
    )
    if obj.config.automatic_upload_on_publish:
        _component_stage(
            config=obj.config,
            components=obj.components,
            distributions=obj.distributions,
            stages=["upload"],
        )


@package.command()
@click.pass_obj
def upload(obj: ContextObj):
    _component_stage(
        config=obj.config,
        components=obj.components,
        distributions=obj.distributions,
        stages=["upload"],
    )


@package.command()
@click.pass_obj
def init_cache(obj: ContextObj):
    _component_stage(
        config=obj.config,
        components=obj.components,
        distributions=obj.distributions,
        stages=["init-cache"],
    )


@package.command()
@click.pass_obj
def diff(obj: ContextObj):
    for component in obj.components:
        if not component.source_dir.exists():
            continue
        status = subprocess.run(
            f"git -C {component.source_dir} status | grep '^nothing to commit'",
            shell=True,
            stdout=subprocess.DEVNULL,
        )
        if not status.returncode == 0:
            subprocess.run(
                f"(echo -e 'Uncommitted changes in {component.source_dir}:\n\n'; git -C {component.source_dir} diff --color=always) | less -RM +Gg",
                shell=True,
            )


# stages commands
package.add_command(init_cache, name="init-cache")
package.add_command(prep)
package.add_command(build)
package.add_command(post)
package.add_command(verify)
package.add_command(sign)
package.add_command(publish)
package.add_command(upload)
package.add_command(_all_package_stage)

# utils commands
package.add_command(diff)

package.add_alias(**STAGES_ALIAS)
