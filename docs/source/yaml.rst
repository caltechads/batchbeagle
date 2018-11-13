===================
YAML file reference
===================


..
    .. contents::

The batchbeagle service config file is a YAML file defining Batch Queues, Compute Environments, and Job Descriptions. The default path for a batchbeagle configuration file is ``./batchbeagle.yml``.

There are currently three main sections in the ``batchbeagle.yml`` file, ``Queues``, ``Compute Environments`` and ``Job Definitions``.

******
Queues
******

Queues are specified in a YAML list under the top level ``queues:`` key like
so::

    queues:
      - name: foobar-prod
        ...
      - name: foobar-test
        ...

name
====

(String, Required) The name of the Batch queue in AWS. ``name`` is required.  There are restrictions on characters:  Up to 255 letters (uppercase and
lowercase), numbers, hyphens, and underscores are allowed.

Once your queue has been created, this is not changable without deleting and
re-creating the queue. ::

    queues:
      - name: foobar-prod

state
=====

(Enum, Required) The state of the job queue. If the job queue state is enabled, it is able to accept jobs. Valid values are ``enabled`` or ``disabled``. ::

    queues:
      - name: foobar-prod
        state: enabled

priority
========

(Integer, Required) The priority of the job queue. Job queues with a higher priority (or a higher integer value for the priority parameter) are evaluated first when associated with same compute environment. Priority is determined in descending order, for example, a job queue with a priority value of 10 is given scheduling preference over a job queue with a priority value of 1. ::

    queues:
      - name: foobar-prod
        state: enabled
        priority: 1

compute_environments
=======================

(List, Required) The set of compute environments mapped to a job queue and their order relative to each other. The job scheduler uses this parameter to determine which compute environment should execute a given job. Compute environments must be in the VALID state before you can associate them with a job queue. You can associate up to 3 compute environments with a job queue. You must specify both the compute environment name and the order. ::

    queues:
      - name: foobar-prod
        state: enabled
        priority: 1
        compute_environments:
          - name: foobar-env
            order: 1

name
----

(String, Required) The name of the compute environment as named in the ``compute_environments`` section.

order
-----

(Integer, Required) The order of the compute environment.

********************
Compute Environments
********************

Compute Environments are specified in a YAML list under the top level ``compute_environments:`` key like so::

    compute_environments:
      - name: foobarenv-prod
        ...
      - name: foobarenv-test
        ...

name
====

(String, Required) The name of the Batch compute environment in AWS. ``name`` is required.  There are restrictions on characters:  Up to 255 letters (uppercase and
lowercase), numbers, hyphens, and underscores are allowed.

Once your compute environment has been created, this is not changable without deleting and
re-creating the compute environment. ::

    compute_environments:
      - name: foobarenv-prod

state
=====

(Enum, Required) The state of the job queue. If the job queue state is enabled, it is able to accept jobs. Valid values are ``enabled`` or ``disabled``. ::

    compute_environments:
      - name: foobarenv-prod
        state: enabled

type
====

(Enum, Required) The type of the compute environment. Valid values are ``managed`` or ``unmanaged``. ::

    compute_environments:
      - name: foobarenv-prod
        state: enabled
        type: managed

serviceRole
===========

(String, Required) The full Amazon Resource Name (ARN) of the IAM role that allows AWS Batch to make calls to other AWS services on your behalf. ::

    compute_environments:
      - name: foobarenv-prod
        state: enabled
        type: managed
        serviceRole: arn:aws:iam::12345678901:role/service-role/AWSBatchServiceRole

compute_resources
=================

Details of the compute resources managed by the compute environment. This parameter is required for managed compute environments. ::

    compute_environments:
      - name: foobarenv-prod
        state: enabled
        type: managed
        serviceRole: arn:aws:iam::12345678901:role/service-role/AWSBatchServiceRole
        compute_resources:
          type: ec2
          instanceRole: arn:aws:iam::12345678901:instance-profile/prodbatchrole
          instanceTypes:
            - optimal
          maxvCpus: 48
          minvCpus: 0
          securityGroupIds:
            - sg-fe1ff599
          subnets:
            - subnet-9f03a2c7

When using Spot instances, you might have something like this::

    compute_environments:
      - name: foobarenv-prod
        state: enabled
        type: managed
        serviceRole: arn:aws:iam::12345678901:role/service-role/AWSBatchServiceRole
        compute_resources:
          type: spot
          instanceRole: arn:aws:iam::12345678901:instance-profile/prodbatchrole
          instanceTypes:
            - optimal
          maxvCpus: 48
          minvCpus: 0
          desiredvCpus: 0
          imageId: foobar
          ec2KeyPair: mykey.pem
          securityGroupIds:
            - sg-fefefefe
          subnets:
            - subnet-9f9f9f9f
          bidPercentage: 50
          spotIamFleetRole: arn:aws:iam::12345678901:role/aws-ec2-spot-fleet-role

type
----

(Enum, Required) The type of compute environment. Valid values are ``ec2`` or ``spot``. ::

    compute_environments:
      - name: foobarenv-prod
        state: enabled
        type: managed
        serviceRole: arn:aws:iam::12345678901:role/service-role/AWSBatchServiceRole
        compute_resources:
            type: ec2

instanceRole
------------

(String, Required) The Amazon ECS instance profile applied to Amazon EC2 instances in a compute environment. You can specify the short name or full Amazon Resource Name (ARN) of an instance profile. For example, ecsInstanceRole or arn:aws:iam::<aws_account_id>:instance-profile/ecsInstanceRole. For more information, see `Amazon ECS Instance Role <http://docs.aws.amazon.com/batch/latest/userguide/instance_IAM_role.html>`_ in the AWS Batch User Guide. ::

    compute_environments:
      - name: foobarenv-prod
        state: enabled
        type: managed
        serviceRole: arn:aws:iam::12345678901:role/service-role/AWSBatchServiceRole
        compute_resources:
            type: ec2
            instanceRole: arn:aws:iam::12345678901:instance-profile/prodbatchrole

instanceTypes
-------------

(List, Required) The instances types that may launched. ::

    compute_environments:
      - name: foobarenv-prod
        state: enabled
        type: managed
        serviceRole: arn:aws:iam::12345678901:role/service-role/AWSBatchServiceRole
        compute_resources:
            type: ec2
            instanceRole: arn:aws:iam::12345678901:instance-profile/prodbatchrole
            instanceTypes:
              - optimal

maxvCpus
--------

(Integer, Required) The maximum number of EC2 vCPUs that an environment can reach.

minvCpus
--------

(Integer, Required) The minimum number of EC2 vCPUs that an environment should maintain.

desiredvCpus
------------

(Integer, Optional) The desired number of EC2 vCPUS in the compute environment.

securityGroupIds
----------------

(List, Required) The EC2 security groups that are associated with instances launched in the compute environment.

subnets
-------

(List, Required) The VPC subnets into which the compute resources are launched.

tags
----

(Dict, Optional) Key-value pair tags to be applied to resources that are launched in the compute environment.

ec2KeyPair
----------

(String, Optional) The EC2 key pair that is used for instances launched in the compute environment.

imageId
-------

(String, Optional) The Amazon Machine Image (AMI) ID used for instances launched in the compute environment.

spotIamFleetRole
----------------

(String, Optional) The Amazon Resource Name (ARN) of the Amazon EC2 Spot Fleet IAM role applied to a SPOT compute environment.

bidPercentage
-------------

(Integer, Optional) The minimum percentage that a Spot Instance price must be when compared with the On-Demand price for that instance type before instances are launched. For example, if your bid percentage is 20%, then the Spot price must be below 20% of the current On-Demand price for that EC2 instance.

***************
Job Definitions
***************

Job Definitions are specified in a YAML list under the top level ``job_definitions:`` key like so::

    job_definitions:
      - name: job1
        ...
      - name: job2
        ...

name
====

(String, Required) The name of the Batch job definition in AWS. ``name`` is required.  There are restrictions on characters:  Up to 255 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. ::

    job_definitions:
      - name: job1

parameters
==========

(Dict, Optional) Default parameter substitution placeholders to set in the job definition. Parameters are specified as a key-value pair mapping. Parameters defined when submitting a job override any corresponding parameter defaults from the job definition. ::

    job_definitions:
      - name: job1
        parameters:
          greeting: hello
          greetee: world

retryStrategy
=============

The retry strategy to use for failed jobs that are submitted with this job definition. ::

    job_definitions:
      - name: job1
        retryStrategy:
            attempts: 1

attempts
--------

(Integer, Optional) The number of times to move a job to the RUNNABLE status. You may specify between 1 and 10 attempts. If attempts is greater than one, the job is retried if it fails until it has moved to RUNNABLE that many times.

timeout
=============

You can configure a timeout duration for your jobs so that if a job runs longer than that, AWS Batch terminates the job. ::

    job_definitions:
      - name: job1
        timeout:
            attemptDurationSeconds: 300

attemptDurationSeconds
--------

(Integer, Optional) The time duration in seconds after which AWS Batch terminates your jobs if they have not finished. The minimum value for the timeout is 60 seconds.

container
=========

Container properties are used in job definitions to describe the container that is launched as part of a job. ::

    job_definitions:
      - name: job1
        container:
          image: centos
          memory: 128
          vcpus: 1
          command: echo nope
          jobRoleArn: arn:aws:iam::12345678901:...
          user: glenn
          privileged: True
          volumes:
            - name: foo
              host:
                sourcePath: bar
            - name: bar
          environment:
            - name: X
              value: 1
            - name: Y
              value: 2
          mountPoints:
            - containerPath: foo1
              readOnly: False
              sourceVolume: bar1
            - containerPath: foo2
              readOnly: True
              sourceVolume: bar2
          ulimits:
            - name: foo
              hardLimit: 15
              softLimit: 7
            - name: bar
              hardLimit: 25
              softLimit: 17


command
-------

(String, Optional) The command that is passed to the container. This parameter maps to Cmd in the Create a container section of the Docker Remote API and the COMMAND parameter to docker run. For more information, see the `Docker Reference <https://docs.docker.com/engine/reference/builder/#cmd>`_


environment
-----------

(Dict, Optional )The environment variables to pass to a container. This parameter maps to Env in the Create a container section of the Docker Remote API and the --env option to docker run.

Important - We do not recommend using plain text environment variables for sensitive information, such as credential data.

Note - Environment variables must not start with AWS_BATCH; this naming convention is reserved for variables that are set by the AWS Batch service.

image
-----

(String, Required) The image used to start a container. This string is passed directly to the Docker daemon. Images in the Docker Hub registry are available by default. Other repositories are specified with repository-url/image:tag . Up to 255 letters (uppercase and lowercase), numbers, hyphens, underscores, colons, periods, forward slashes, and number signs are allowed. This parameter maps to Image in the Create a container section of the Docker Remote API and the IMAGE parameter of docker run. Images in Amazon ECR repositories use the full registry and repository URI (for example, 012345678910.dkr.ecr.<region-name>.amazonaws.com/<repository-name>).

jobRoleArn
----------

(String, Optional) The Amazon Resource Name (ARN) of the IAM role that the container can assume for AWS permissions.

memory
------

(Integer, Required) The hard limit (in MiB) of memory to present to the container. If your container attempts to exceed the memory specified here, the container is killed. This parameter maps to Memory in the Create a container section of the Docker Remote API and the --memory option to docker run. You must specify at least 4 MiB of memory for a job.

privileged
----------

(Boolean, Optional) When this parameter is True, the container is given elevated privileges on the host container instance (similar to the root user). This parameter maps to Privileged in the Create a container section of the Docker Remote API and the --privileged option to docker run.

readonlyRootFilesystem
----------------------

(Boolean, Optional) When this parameter is true, the container is given read-only access to its root file system. This parameter maps to ReadonlyRootfs in the Create a container section of the Docker Remote API and the --read-only option to docker run.

user
----

(String, Optional) The user name to use inside the container. This parameter maps to User in the Create a container section of the Docker Remote API and the --user option to docker run.

vcpus
-----

(Integer, Required) The number of vCPUs reserved for the container. This parameter maps to CpuShares in the Create a container section of the Docker Remote API and the --cpu-shares option to docker run. Each vCPU is equivalent to 1,024 CPU shares. You must specify at least 1 vCPU.

mountPoints
-----------

(List, Optional) The mount points for data volumes in your container. This parameter maps to Volumes in the Create a container section of the Docker Remote API and the --volume option to docker run.

containerPath
^^^^^^^^^^^^^

(String, Optional) The path on the container at which to mount the host volume.

readOnly
^^^^^^^^

(Boolean, Optional) If this value is True, the container has read-only access to the volume; otherwise, the container can write to the volume. The default value is False.

sourceVolume
^^^^^^^^^^^^

(String, Optional) The name of the volume to mount.

ulimits
-------

(List, Optional) A list of ulimits to set in the container. This parameter maps to Ulimits in the Create a container section of the Docker Remote API and the --ulimit option to docker run.

name
^^^^

(String, Required) The type of the ulimit.

hardLimit
^^^^^^^^^

(Integer, Required) The hard limit for the ulimit type.


softLimit
^^^^^^^^^

(Integer, Required) The soft limit for the ulimit type.

volumes
-------

(List, Optional) A list of data volumes used in a job.

name
^^^^

(String, Optional) The name of the volume. Up to 255 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. This name is referenced in the sourceVolume parameter of container definition mountPoints.

host
^^^^

(Dict, Optional) The contents of the host parameter determine whether your data volume persists on the host container instance and where it is stored. If the host parameter is empty, then the Docker daemon assigns a host path for your data volume, but the data is not guaranteed to persist after the containers associated with it stop running.

sourcePath
^^^^^^^^^^

(String, Optional) The path on the host container instance that is presented to the container. If this parameter is empty, then the Docker daemon has assigned a host path for you. If the host parameter contains a sourcePath file location, then the data volume persists at the specified location on the host container instance until you delete it manually. If the sourcePath value does not exist on the host container instance, the Docker daemon creates it. If the location does exist, the contents of the source path folder are exported.

***************
Variable interpolation in batchbeagle.yml
***************

You can use variable replacement in your job definitions to dynamically replace values from your local shell environment.

You can add ``${env.<environment var>}`` to your service definition anywhere you want the value of the shell environment variable ``<environment var>``. For example, for the following ``batchbeagle.yml`` snippet::

    job_definitions:
      - name: test-job-001
        container:
          image: ${env.IMG_NAME}:${env.IMG_VERSION}
          memory: 10
          vcpus: 1

batchbeagle –import_env command line option
====

If you run ``batchbeagle`` with the ``--import_env`` option, it will import your shell environment into the batchbeagle environment. Then anything you’ve defined in your shell environment will be available for ``${env.VAR}`` replacements.

Example::

    batchbeagle --import_env <subcommand> [options]
