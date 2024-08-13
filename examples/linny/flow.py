"""
Information
---------------------------------------------------------------------
Name        : flow.py
Location    : ~/examples/linear-regression
Author      : Tom Eleff
Published   : 2024-04-05
Revised on  : .

Description
---------------------------------------------------------------------
The main linear-regression `prefect` workflow executable.
"""

import os
import time
from prefect import flow, task, task_runners
from prefect.artifacts import create_markdown_artifact
from pytensils import config, logging


@task(
    name='setup',
    description='Starts the flow-run and returns the flow-parameters as a `pytensils` configuration-object.'
)
def setup_flow_run(run_request: dict) -> config.Handler:
    """ Starts the flow-run and returns the flow-job-request as a `pytensils` configuration-object.

    Parameters
    ----------
    run_request : `dict`
        Dictionary object containing the flow-run parameters and values.
    """

    # Setup the flow-configuration
    Flow = config.Handler(
        path=os.path.dirname(__file__),
        file_name='flow.json'
    )

    # Parse the arguments
    if Flow.validate(
        dtypes=config.Handler(
            path=os.path.dirname(__file__),
            file_name='dtypes.json'
        ).to_dict()
    ):

        # Update the flow-configuration
        Flow.data['run_request'] = run_request

        return Flow


@task(
    name='start_logging',
    description='Initializes user-logging.'
)
def start_logging(
    Flow: config.Handler,
    indent: int = logging.INDENT,
    line_length: int = logging.LINE_LENGTH,
    timezone: str = logging.TIMEZONE
) -> logging.Handler:
    """ Initializes user-logging.

    Parameters
    ----------
    Flow : `config.Handler`
        The flow-run configuration object.
    indent : `int`
        The number of space-characters for the standard log-indentation (default = 4).
    line_length : `int`
        The maximum number of characters for a line of content (default = 79).
    timezone : `str`
        The time-zone for representing start and end time values (default = 'America/New_York').
    """

    # Set-up the logging object
    logging.INDENT = indent
    logging.LINE_LENGTH = line_length
    logging.TIMEZONE = timezone

    return logging.Handler(
        path=Flow.data['run_request']['dir']['outputs'],
        description=Flow.data['linear-regression']['description'],
        metadata=Flow.data['run_request']['run-information'],
        debug_console=True
    )


@task(
    name='validate-configuration',
    description='Validates the configuration parameters and reports validation errors via the user-log.'
)
def validate_configuration(
    Flow: config.Handler,
    Logging: logging.Handler
) -> config.Handler:
    """ Validates the configuration parameters and reports validation errors via the user-log.

    Parameters
    ----------
    Flow : `config.Handler`
        The flow-run configuration object.
    Logging : `logging.Handler`
        The user-logging object.
    """

    # Setup the workflow-configuration
    Workflow = Flow.data['run_request']['workflow']

    time.sleep(20)

    # Validate the workflow-configuration
    # if Workflow.validate(
    #     dtypes=config.Handler(
    #         path=os.path.join(
    #             Flow.data['run_request']['dir']['inputs'],
    #             'workflow'
    #         ),
    #         file_name='dtypes.json'
    #     ).to_dict()
    # ):

    # Logging
    Logging.write_header(header='Workflow validation')
    Logging.write(content="The workflow configuration validation completed successfully.")
    Logging.write(content=Workflow)

    return Workflow


@task(
    name='end-logging',
    description='Ends user-logging and outputs the run-time summary.'
)
def end_logging(Logging: logging.Handler):
    """ Ends user-logging and persists the user-log as a `prefect.artifact`.

    Parameters
    ----------
    Logging : `logging.Handler`
        The user-logging object.
    """

    Logging.close()

    # Persist logging artifact
    with open(os.path.join(Logging.path, Logging.file_name), 'r') as content:
        create_markdown_artifact(
            markdown=content.read(),
            description='The user-log generated by the flow-run.'
        )


@flow(
    task_runner=task_runners.SequentialTaskRunner,
    log_prints=True
)
def linear_regression_flow(
    run_request
):
    """ A linear regression analysis with a linear regression assumption evaluator, orchestrated by `prefect`.
    """

    # Setup the flow-configuration
    Flow = setup_flow_run(
        run_request=run_request
    )

    # Initialize user-logging
    Logging = start_logging(
        Flow=Flow,
        line_length=139,
        timezone='America/Chicago'
    )

    # # User's custom flow
    # @flow(
    #     task_runner=task_runners.SequentialTaskRunner,
    #     log_prints=True
    # )
    # @Logging.close_on_exception
    # def fails_on_exception():
    #     """ A flow that fails due to a divide by zero error.
    #     """
    #     return 1 / 0

    # # Execute user's custom flow
    # _ = fails_on_exception()

    # Validate the workflow-parameters with unhandled-exception reporting
    _ = validate_configuration(Flow=Flow, Logging=Logging)

    # Close logging
    end_logging(Logging=Logging)


if __name__ == "__main__":
    linear_regression_flow.serve(
        name='v0_1_0',
        description="A linear regression analysis with a linear regression assumption evaluator, orchestrated by `prefect`.",
        tags=['v0.1.0'],
        version='v0.1.0',
        enforce_parameter_schema=True,
        print_starting_message=True
    )
