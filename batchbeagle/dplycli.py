#!/usr/bin/env python

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
    mgr.destroy_compute_environment(compute_environment)

@cli.group(short_help='Work with Batch Jobs.')
def job():
    """
    Sub-command for building and managing Batch job descriptiouns and jobs.
    """
    pass

@job.command()
@click.pass_context
@click.argument('name')
@click.argument('job_description')
@click.argument('queue')
@click.option('--parameters', '-p', default=None, help="Path to the parameters file.")
def submit(ctx, name, job_description, queue, parameters):
    """
    Submit jobs to AWS Batch. Each line of the parameters file will result in a job.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    if parameters:
        with open(parameters) as csvfile:
            # first line is parameter names
            reader = csv.DictReader(csvfile)
            for row in reader:
                mgr.submit_job(name, job_description, queue, parameters=row)
    else:
        mgr.submit_job(name, job_description, queue)
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
@click.argument('job_description')
def create(ctx, job_description):
    """
    Create a new job description.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.create_job_description(job_description)

@job.command()
@click.pass_context
@click.argument('job_description')
def update(ctx, job_description):
    """
    Update an existing job description.
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.update_job_description(job_description)

@job.command()
@click.pass_context
@click.argument('job_description')
def deregister(ctx, job_description):
    """
    Deregister an existing job description.
    :param ctx:
    :param job_description:
    :return:
    """
    mgr = BatchManager(filename=ctx.obj['CONFIG_FILE'])
    mgr.deregister_job_description(job_description)

def main():
    cli(obj={})


if __name__ == '__main__':
    main()