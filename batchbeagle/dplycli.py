#!/usr/bin/env python

import copy
import csv
import time

import click

from batchbeagle.config import Config
from batchbeagle.aws.batch import BatchManager, Queue

@click.group()
@click.option('--filename', '-f', default='batchbeagle.yml', help="Path to the config file. Default: ./batchbeagle.yml")
@click.pass_context
def cli(ctx, filename):
    """
    Configure and deploy AWS Batch jobs.
    """
    ctx.obj['CONFIG_FILE'] = filename

@cli.command()
@click.pass_context
def info(ctx):
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    lines = mgr.describe()
    for line in lines:
        click.echo(line)

@cli.group(short_help='Work with Batch Queues.')
def queue():
    """
    Sub-command for building and managing queues.
    """
    pass

@queue.command(short_help="Create a new queue.")
@click.pass_context
@click.argument('queue')
def create(ctx, queue):
    """
    Create a new queue.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.create_queue(queue)

@queue.command()
@click.pass_context
@click.argument('queue')
def update(ctx, queue):
    """
    Update an existing queue.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.update_queue(queue)

@queue.command()
@click.pass_context
@click.argument('queue')
def disable(ctx, queue):
    """
    Disable an existing queue.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.disable_queue(queue)

@queue.command()
@click.pass_context
@click.argument('queue')
def destroy(ctx, queue):
    """
    Destroy an existing queue.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.disable_queue(queue)
    time.sleep(1)
    mgr.destroy_queue(queue)

@cli.group(short_help='Work with Batch Compute Environments.')
def compute():
    """
    Sub-command for building and managing Batch compute environments.
    """
    pass

@compute.command()
@click.pass_context
@click.argument('compute_environment')
def create(ctx, compute_environment):
    """
    Create a new compute environment.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.create_compute_environment(compute_environment)

@compute.command()
@click.pass_context
@click.argument('compute_environment')
def update(ctx, compute_environment):
    """
    Update an existing compute environment.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.update_compute_environment(compute_environment)

@compute.command()
@click.pass_context
@click.argument('compute_environment')
def disable(ctx, compute_environment):
    """
    Disable an existing compute environment.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.disable_compute_environment(compute_environment)

@compute.command()
@click.pass_context
@click.argument('compute_environment')
def destroy(ctx, compute_environment):
    """
    Destroy an existing compute environment.
    """

    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.disable_compute_environment(compute_environment)
    time.sleep(1)
    mgr.destroy_compute_environment(compute_environment)

@cli.group(short_help='Work with Batch Jobs.')
def job():
    """
    Sub-command for building and managing Batch job definitions and jobs.
    """
    pass

@job.command()
@click.pass_context
@click.argument('name')
@click.argument('job_definition')
@click.argument('queue')
@click.option('--parameters', '-p', default=None, help="Path to the parameters file.")
@click.option('--nowait', is_flag=True, default=False, help="Do not wait for all jobs to start running")
def submit(ctx, name, job_definition, queue, parameters, nowait):
    """
    Submit jobs to AWS Batch. Each line of the parameters file will result in a job.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    if parameters:
        with open(parameters) as csvfile:
            # first line is parameter names
            reader = csv.DictReader(csvfile)
            for row in reader:
                mgr.submit_job(name, job_definition, queue, parameters=row)
    else:
        mgr.submit_job(name, job_definition, queue)
    while True:
        lines, runnable_count = mgr.list_jobs(queue)
        for line in lines:
            click.echo(line)
        if runnable_count == 0 or nowait:
            break
        time.sleep(5)


@job.command()
@click.pass_context
@click.argument('queue')
def list(ctx, queue):
    """
    List running jobs.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    lines, runnable_count = mgr.list_jobs(queue)
    for line in lines:
        click.echo(line)

@job.command()
@click.pass_context
@click.argument('queue')
def cancel(ctx, queue):
    """
    Cancel all jobs.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.cancel_all_jobs(queue)
    while True:
        lines, runnable_count = mgr.list_jobs(queue)
        for line in lines:
            click.echo(line)
        if runnable_count == 0:
            break
        time.sleep(5)

@job.command()
@click.pass_context
@click.argument('queue')
def terminate(ctx, queue):
    """
    Terminate all jobs.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.terminate_all_jobs(queue)
    while True:
        lines, runnable_count = mgr.list_jobs(queue)
        for line in lines:
            click.echo(line)
        if runnable_count == 0:
            break
        time.sleep(5)

@job.command()
@click.pass_context
@click.argument('job_definition')
def create(ctx, job_definition):
    """
    Create a new job definition.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.create_job_definition(job_definition)

@job.command()
@click.pass_context
@click.argument('job_definition')
def update(ctx, job_definition):
    """
    Update an existing job definition.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.update_job_definition(job_definition)

@job.command()
@click.pass_context
@click.argument('job_definition')
def deregister(ctx, job_definition):
    """
    Deregister an existing job definition.
    :param ctx:
    :param job_definition:
    :return:
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.deregister_job_definition(job_definition)

@cli.command(short_help='Assemble all Batch resoures defined in a configuration')
@click.pass_context
def assemble(ctx):
    """
    Assemble (create/update) all Job Descriptions, Job Queues and Compute Environments in a config file
    :param ctx:
    :return:
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.assemble()

@cli.command(short_help='Teardown all Batch resoures defined in a configuration')
@click.pass_context
def teardown(ctx):
    """
    Teardown (destroy/deregister) all Job Descriptions, Job Queues and Compute Environments in a config file
    :param ctx:
    :return:
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.teardown()

def main():
    cli(obj={})


if __name__ == '__main__':
    main()
