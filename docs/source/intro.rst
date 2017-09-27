Introduction
============

.. include:: quickintro.rst

To use ``batchbeagle``, you

* Install ``batchbeagle``
* Define your queues, compute environments, and job descriptions in ``batchbeagle.yml``
* Use ``beagle`` to start managing them

A simple ``batchbeagle.yml`` looks like this::

    queues:
      - name: queue1
        state: enabled
        priority: 1
        compute_environments:
          - name: env1
            order: 1

    compute_environments:
      - name: env1
        type: managed
        state: enabled
        serviceRole: arn:aws:iam::12345678901:role/service-role/AWSBatchServiceRole
        compute_resources:
            type: spot
            instanceRole: arn:aws:iam::12345678901:instance-profile/env1
            instanceTypes:
              - optimal
            maxvCpus: 24
            minCpus: 0
            securityGroupIds:
              - sg-ffffffff
            subnets:
              - subnet-9f9f9f

    job_definitions:
      - name: job1
        container:
            image: centos
            memory: 128
            vcpus: 1
            command: echo ${greeting} ${greetee}
        parameters:
            greeting: hello
            greetee: world

