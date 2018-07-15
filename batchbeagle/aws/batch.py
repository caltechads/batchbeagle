from __future__ import print_function

import boto3
import csv
import sys
import time
import yaml

BATCH_CLIENT = None

def get_batch_client():
    global BATCH_CLIENT
    if not BATCH_CLIENT:
        BATCH_CLIENT = boto3.client('batch')
    return BATCH_CLIENT

class AWSRenderable(object):

    def __init__(self, limited_update=False):
        self.data = {}
        self.update_data = {}
        self.limited_update = limited_update

    def _add_key(self, key, value=None, in_update=False, only_in_update=False):
        if value or value == 0 or value == False:
            self.data[key] = value
        else:
            value = getattr(self, key, None)
            if value or value == 0:
                self.data[key] = value

        if self.limited_update and in_update and key in self.data:
            self.update_data[key] = self.data[key]
            if only_in_update:
                del self.data[key]

    def load_render(self):
        pass

    def render(self, update=False):
        self.load_render(update)
        if update and self.limited_update:
            return self.update_data
        return self.data

    def _describe_if_exists(self, attribute, description, force=False):
        if force or (hasattr(self, attribute) and getattr(self, attribute)):
            description.append("{}: {}".format(attribute, getattr(self, attribute)))


class AWSLimitedUpdateRenderable(AWSRenderable):

    def __init__(self):
        super(AWSLimitedUpdateRenderable, self).__init__(True)


class JobContainerVolume(AWSRenderable):


    def __init__(self, yml={}):
        super(JobContainerVolume, self).__init__()
        self.from_yaml(yml)

    def from_yaml(self, yml):
        self.name = yml['name']
        self.host = yml.get('host', {})

    def load_render(self, update):
        self._add_key('name')
        self._add_key('host')

    def describe(self):
        description = []
        self._describe_if_exists('name', description)
        self._describe_if_exists('host', description)
        return description


class JobContainerMountPoint(AWSRenderable):


    def __init__(self, yml={}):
        super(JobContainerMountPoint, self).__init__()
        self.from_yaml(yml)

    def from_yaml(self, yml):
        self.containerPath = yml['containerPath']
        self.readOnly = yml['readOnly']
        self.sourceVolume = yml['sourceVolume']

    def load_render(self, update):
        self._add_key('containerPath')
        self._add_key('readOnly')
        self._add_key('sourceVolume')

    def describe(self):
        description = []
        self._describe_if_exists('containerPath', description)
        self._describe_if_exists('readOnly', description, True)
        self._describe_if_exists('sourceVolume', description)
        return description


class JobContainerULimit(AWSRenderable):


    def __init__(self, yml={}):
        super(JobContainerULimit, self).__init__()
        self.from_yaml(yml)

    def from_yaml(self, yml):
        self.name = yml['name']
        self.hardLimit = yml['hardLimit']
        self.softLimit = yml['softLimit']

    def load_render(self, update):
        self._add_key('name')
        self._add_key('hardLimit')
        self._add_key('softLimit')

    def describe(self):
        description = []
        self._describe_if_exists('name', description)
        self._describe_if_exists('hardLimit', description)
        self._describe_if_exists('softLimit', description)
        return description


class JobContainer(AWSRenderable):

    def __init__(self, yml={}):
        super(JobContainer, self).__init__()
        self.volumes = []
        self.environment = []
        self.mount_points = []
        self.ulimits = []
        self.from_yaml(yml)

    def from_yaml(self, yml):
        self.image = yml['image']
        self.memory = yml['memory']
        self.vcpus = yml['vcpus']
        self.command = yml.get('command', '')
        self.jobRoleArn = yml.get('jobRoleArn', '')
        self.readonlyRootFilesystem = yml.get('readonlyRootFilesystem', None)
        self.privileged = yml.get('privileged', None)
        self.user = yml.get('user', None)
        if 'volumes' in yml:
            for vol in yml['volumes']:
                self.volumes.append(JobContainerVolume(vol))
        if 'environment' in yml:
            for env in yml['environment']:
                self.environment.append({'name': env['name'], 'value': env['value']})
        if 'mountPoints' in yml:
            for mp in yml['mountPoints']:
                self.mount_points.append(JobContainerMountPoint(mp))
        if 'ulimits' in yml:
            for ulimit in yml['ulimits']:
                self.ulimits.append(JobContainerULimit(ulimit))

    def load_render(self, update):
        self._add_key('image')
        self._add_key('memory')
        self._add_key('vcpus')
        self._add_key('command', self._replace_command())
        self._add_key('jobRoleArn')
        self._add_key('readonlyRootFilesystem')
        self._add_key('privileged')
        self._add_key('user')
        volumes = []
        for vol in self.volumes:
            volumes.append(vol.render(update))
        self._add_key('volumes', volumes)
        self._add_key('environment', self.environment)
        mount_points = []
        for mp in self.mount_points:
            mount_points.append(mp.render(update))
        self._add_key('mountPoints', mount_points)
        ulimits = []
        for ulimit in self.ulimits:
            ulimits.append(ulimit.render(update))
        self._add_key('ulimits', ulimits)

    def _replace_command(self):
        args = self.command.split()
        command = []
        for arg in args:
            if arg.startswith("${"):
                parameter = arg[2:-1]
                command.append("Ref::{}".format(parameter))
            else:
                command.append(arg)
        return command

    def describe(self):
        description = []
        description.append("image: {}".format(self.image))
        description.append("memory: {}".format(self.memory))
        description.append("vcpus: {}".format(self.vcpus))
        description.append("command: {}".format(self.command))
        self._describe_if_exists('jobRoleArn', description)
        self._describe_if_exists('readonlyRootFilesystem', description)
        self._describe_if_exists('privileged', description)
        self._describe_if_exists('user', description)
        if self.volumes:
            description.append("Volumes:")
            for vol in self.volumes:
                lines = vol.describe()
                description.append("  - {}".format(lines[0]))
                for line in lines[1:]:
                    description.append('    {}'.format(line))
        if self.environment:
            description.append("Environment:")
            for env in self.environment:
                description.append("  - name: {}".format(env['name']))
                description.append("    value: {}".format(env['value']))
        if self.mount_points:
            description.append("Mount Points:")
            for mp in self.mount_points:
                lines = mp.describe()
                description.append("  - {}".format(lines[0]))
                for line in lines[1:]:
                    description.append('    {}'.format(line))
        if self.ulimits:
            description.append("ULimits:")
            for ulimit in self.ulimits:
                lines = ulimit.describe()
                description.append("  - {}".format(lines[0]))
                for line in lines[1:]:
                    description.append('    {}'.format(line))

        return description


class JobDefinition(AWSRenderable):

    def __init__(self, yml={}):
        super(JobDefinition, self).__init__()
        self.batch = get_batch_client()
        self.from_yaml(yml)
        self.__aws_j = None
        self.arn = None
        self.revision = 0

    def from_yaml(self, yml):
        self.name = yml['name']
        self.container = JobContainer(yml['container'])
        self.parameters = yml.get('parameters', None)
        self.retryStrategy = yml.get('retryStrategy', None)

    def load_render(self, update):
        self._add_key('jobDefinitionName', self.name)
        self._add_key('type', 'container')
        self._add_key('containerProperties', self.container.render(update))
        self._add_key('parameters')
        self._add_key('retryStrategy')

    def _get_all_active(self):
        active = []
        nextToken = ''
        while True:
            response = self.batch.describe_job_definitions(
                jobDefinitionName=self.name,
                status='ACTIVE',
                nextToken = nextToken
            )
            if 'jobDefinitions' in response and response['jobDefinitions']:
                for jd in response['jobDefinitions']:
                    arn = jd['jobDefinitionArn']
                    active.append(arn)
            nextToken = response.get('nextToken', None)
            if not nextToken:
                break
        return active


    def deregister(self):
        active = self._get_all_active()
        for jd in active:
            response = self.batch.deregister_job_definition(jobDefinition=jd)

    def register(self):
        self.deregister()
        kwargs = self.render()
        response = self.batch.register_job_definition(**kwargs)
        self.arn = response['jobDefinitionArn']
        self.revision = response['revision']

    def __getattr__(self, attr):
        """
        We have this __getattr__ here to access some attributes on the dict that AWS
        returns to us via the ``describe_compute_environments()`` call.
        """
        try:
            return self.__getattribute__(attr)
        except AttributeError:
            if attr in ['arn', 'status', 'statusReason', 'ecsClusterArn', 'serviceRole']:
                if self.__aws_compute_environment:
                    return self.__aws_compute_environment[self._map_attr(attr)]
                return None
            else:
                raise AttributeError

    def __get_job_definition(self):
        nextToken = ''

        while True:
            response = self.batch.describe_job_definition(
                jobDefinitionName=self.name,
                status='ACTIVE'
            )
            if 'jobDefinitions' in response and response['jobDefinitions']:
                return response['jobDefinitions'][0]
            else:
                return {}

    def from_aws(self):
        self.__aws_job = ""

    def describe(self):
        description = []
        description.append("name: {}".format(self.name))
        description.append("arn: {}".format(self.arn))
        description.append("revision: {}".format(self.revision))
        if self.parameters:
            description.append("parameters: {}".format(', '.join(self.parameters)))
        description.append("Container Properties")
        properties = self.container.describe()
        for prop in properties:
            description.append("  {}".format(prop))
        if self.retryStrategy:
            description.append("Retry Strategy")
            description.append("  attempts: {}".format(self.retryStrategy['attempts']))
        return description


class ComputeResources(AWSLimitedUpdateRenderable):

    def __init__(self, yml={}):
        super(ComputeResources, self).__init__()
        self.batch = get_batch_client()
        if yml:
            self.from_yaml(yml)

    def from_yaml(self, yml):
        self.type = yml['type'].upper()
        self.subnets = yml['subnets']
        self.instanceRole = yml['instanceRole']
        self.instanceTypes = yml['instanceTypes']
        self.maxvCpus = yml['maxvCpus']
        self.minvCpus = yml['minvCpus']
        self.desiredvCpus = yml.get('desiredvCpus', '')
        self.imageId = yml.get('imageId', '')
        self.ec2KeyPair = yml.get('ec2KeyPair', '')
        self.tags = yml.get('tags', None)
        self.securityGroupIds = yml['securityGroupIds']
        self.bidPercentage = yml.get('bidPercentage', '')
        self.spotIamFleetRole = yml.get('spotIamFleetRole', '')

    def load_render(self, update):
        self._add_key('type')
        self._add_key('minvCpus', in_update=True)
        self._add_key('maxvCpus', in_update=True)
        self._add_key('desiredvCpus', in_update=True)
        self._add_key('instanceTypes')
        self._add_key('subnets')
        self._add_key('securityGroupIds')
        self._add_key('instanceRole')
        self._add_key('imageId')
        self._add_key('ec2KeyPair')
        self._add_key('tags')
        if self.type == 'SPOT':
            self._add_key('bidPercentage')
            self._add_key('spotIamFleetRole')

    def __getattr__(self, attr):
        """
        We have this __getattr__ here to access some attributes on the dict that AWS
        returns to us via the ``describe_compute_environments()`` call.
        """
        try:
            return self.__getattribute__(attr)
        except AttributeError:
            if attr in ['arn', 'state', 'status', 'statusReason', 'ecsClusterArn']:
                if self.__aws_compute_environment:
                    return self.__aws_compute_environment[self._map_attr(attr)]
                return None
            else:
                raise AttributeError

    def from_aws(self, aws):
        self.__aws_compute_resources = aws

    def describe(self):
        description = ["Compute Resources:"]
        description.append("type: {}".format(self.type))
        description.append("instanceRole: {}".format(self.instanceRole))
        description.append("maxvCpus: {}".format(self.maxvCpus))
        description.append("minvCpus: {}".format(self.minvCpus))
        description.append("subnets: {}".format(', '.join(self.subnets)))
        description.append("instanceTypes: {}".format(', '.join(self.instanceTypes)))
        description.append("securityGroupIds: {}".format(', '.join(self.securityGroupIds)))
        self._describe_if_exists('desiredvCpus', description, True)
        self._describe_if_exists('imageId', description)
        self._describe_if_exists('ec2KeyPair', description)
        self._describe_if_exists('tags', description)
        return description


class ComputeEnvironment(AWSLimitedUpdateRenderable):

    ATTR_MAPPING = {
        'arn': 'computeEnvironmentArn'
    }

    MANAGED = 'MANAGED'

    def __init__(self, yml={}):
        super(ComputeEnvironment, self).__init__()
        self.batch = get_batch_client()
        self.from_yaml(yml)
        self.order = 0

    def load_render(self, update):
        self._add_key('computeEnvironment', self.arn, True, True)
        self._add_key('computeEnvironmentName', self.name)
        self._add_key('type')
        self._add_key('state', in_update=True)
        self._add_key('serviceRole', in_update=True)
        if self.compute_resources:
            self._add_key('computeResources', self.compute_resources.render(update), in_update=True)

    def _map_attr(self, attr):
        if attr in self.ATTR_MAPPING:
            return self.ATTR_MAPPING[attr]
        return attr

    def __getattr__(self, attr):
        """
        We have this __getattr__ here to access some attributes on the dict that AWS
        returns to us via the ``describe_compute_environments()`` call.
        """
        try:
            return self.__getattribute__(attr)
        except AttributeError:
            if attr in ['arn', 'status', 'statusReason', 'ecsClusterArn', 'serviceRole']:
                if self.__aws_compute_environment:
                    return self.__aws_compute_environment[self._map_attr(attr)]
                return None
            else:
                raise AttributeError

    def from_yaml(self, yml):
        self.name = yml['name']
        self.type = yml['type'].upper()
        if 'state' in yml:
            self.state = yml['state'].upper()
        else:
            self.state = 'ENABLED'
        self.serviceRole = yml['serviceRole']
        if self.type == self.MANAGED:
            self.compute_resources = ComputeResources(yml['compute_resources'])
        else:
            self.compute_resources = None
        self.__aws_compute_environment = None

    def __get_compute_environment(self):
        response = self.batch.describe_compute_environments(
            computeEnvironments=[self.name]
        )
        if 'computeEnvironments' in response and response['computeEnvironments']:
            return response['computeEnvironments'][0]
        else:
            return {}

    def from_aws(self, aws):
        self.__aws_compute_environment = aws

    def aws_state(self):
        if self.exists():
            return self.__aws_compute_environment['state']

    def exists(self):
        if self.__aws_compute_environment:
            return True
        return False

    def set_order(self, order):
        self.order = order

    def describe(self):
        if not self.__aws_compute_environment:
            return []
        description = []
        description.append("name: {}".format(self.name))
        description.append("type: {}".format(self.type))
        if self.__aws_compute_environment:
            description.append("arn: {}".format(self.arn))
            description.append("order: {}".format(self.order))
            description.append("serviceRole: {}".format(self.serviceRole))
            description.append("state: {}".format(self.__aws_compute_environment['state']))
            description.append("status: {}".format(self.status))
        if self.type == self.MANAGED:
            resource_description = self.compute_resources.describe()
            description.append(resource_description[0])
            for line in resource_description[1:]:
                description.append("  {}".format(line))
        description.append("serviceRole: {}".format(self.serviceRole))

        return description


class ComputeEnvironmentOrder(AWSRenderable):

    def __init__(self, yml):
        super(ComputeEnvironmentOrder, self).__init__()
        self.order = yml['order']
        self.name = yml['name']
        self.arn = ""

    def load_render(self, update):
        self._add_key('computeEnvironment', self.arn)
        self._add_key('order')

    def set_arn(self, arn):
        self.arn = arn

    def describe(self):
        description = []
        description.append("name: {}".format(self.name))
        description.append("order: {}".format(self.order))
        description.append("arn: {}".format(self.arn))
        return description

class Queue(AWSLimitedUpdateRenderable):

    ATTR_MAPPING = {
        'arn': 'jobQueueArn'
    }

    def __init__(self, yml={}):
        super(Queue, self).__init__()
        self.compute_environments = {}
        self.job_definitions = []
        self.from_yaml(yml)
        self.__aws_queue = None
        # self.from_aws()

    def load_render(self, update):
        ceos = []
        for ceo in self.compute_environments.values():
            ceos.append(ceo.render(update))
        self._add_key('computeEnvironmentOrder', ceos, True)
        self._add_key('jobQueue', self.arn, True, True)
        self._add_key('jobQueueName', self.name)
        self._add_key('priority', in_update=True)
        self._add_key('state', in_update=True)

    def from_yaml(self, yml):
        """
        Load our queue information from the parsed yaml.  ``yml`` should be
        a queue level entry from the ``batchbeagle.yml`` file.

        :param yml: a queue level entry from the ``batchbeagle.yml`` file
        :type yml: dict
        """
        self.name = yml['name']
        self.state = yml['state'].upper()
        self.priority = yml['priority']
        if 'compute_environments' in yml:
            for compenv in yml['compute_environments']:
                self.compute_environments[compenv['name']] = ComputeEnvironmentOrder(compenv)
        # if 'job_definitions' in yml:
        #     for job in yml['job_definitions']:
        #         self.job_definitions.append(JobDefinition(job))

    def __get_queue(self):
        response = self.batch.describe_job_queues(
            jobQueues=[self.name]
        )
        if 'jobQueues' in response and response['jobQueues']:
            return response['jobQueues'][0]
        else:
            return {}

    def _map_attr(self, attr):
        if attr in self.ATTR_MAPPING:
            return self.ATTR_MAPPING[attr]
        return attr

    def __getattr__(self, attr):
        """
        We have this __getattr__ here to access some attributes on the dict that AWS
        returns to us via the ``describe_job_queues()`` call.
        """
        try:
            return self.__getattribute__(attr)
        except AttributeError:
            if attr in ['arn', 'state', 'status', 'statusReason', 'priority']:
                if self.__aws_queue:
                    return self.__aws_queue[self._map_attr(attr)]
                return None
            else:
                raise AttributeError

    def from_aws(self, aws):
        """
        Update our queue, jobs, job definitions, and compute environments from the live
        versions in AWS.
        """
        self.__aws_queue = aws

    def aws_state(self):
        if self.exists():
            return self.__aws_queue['state']

    def update_compute_environments(self, aws_compute_environments):
        for env in aws_compute_environments:
            for name, env_order in self.compute_environments.items():
                if name ==  env['computeEnvironmentName']:
                    env_order.arn = env['computeEnvironmentArn']
                    break

    def exists(self):
        if self.__aws_queue:
            return True
        return False

    def describe(self):
        if not self.__aws_queue:
            return []
        description = []
        description.append("name: {}".format(self.name))
        if self.__aws_queue:
            description.append("arn: {}".format(self.__aws_queue['jobQueueArn']))
            description.append("state: {}".format(self.__aws_queue['state']))
            description.append("status: {}".format(self.__aws_queue['status']))
            description.append("statusReason: {}".format(self.__aws_queue['statusReason']))
            description.append("priority: {}".format(self.__aws_queue['priority']))
        description.append('Compute Environments:')
        for env in self.compute_environments.values():
            env_description = env.describe()
            description.append("  - {}".format(env_description[0]))
            for line in env_description[1:]:
                description.append("    {}".format(line))
        return description


class BatchManager(object):

    def __init__(self, filename='batchbeagle.yml'):
        self.batch = get_batch_client()
        self.queues = {}
        self.compute_environments = {}
        self.job_definitions = {}
        self.yml = self.load_config(filename)
        self.from_yaml()
        self.from_aws()

    def load_config(self, filename):
        with open(filename) as f:
            return yaml.load(f)

    def from_yaml(self):
        if 'queues' in self.yml:
            for qml in self.yml['queues']:
                queue = Queue(qml)
                self.queues[queue.name] = queue

        if 'compute_environments' in self.yml:
            for cml in self.yml['compute_environments']:
                env = ComputeEnvironment(cml)
                self.compute_environments[env.name] = env

        if 'job_definitions' in self.yml:
            for jml in self.yml['job_definitions']:
                jd = JobDefinition(jml)
                self.job_definitions[jd.name] = jd

    def __get_queues(self):
        response = self.batch.describe_job_queues(
            jobQueues=list(self.queues)
        )
        if 'jobQueues' in response and response['jobQueues']:
            return response['jobQueues']
        else:
            return {}

    def __get_compute_environments(self):
        compute_environments = list(self.compute_environments)
        for name, queue in self.queues.items():
            for env in queue.compute_environments.values():
                if env.name not in self.compute_environments:
                    compute_environments.append(env.name)

        response = self.batch.describe_compute_environments(
            computeEnvironments=compute_environments
        )
        if 'computeEnvironments' in response and response['computeEnvironments']:
            return response['computeEnvironments']
        else:
            return {}

    def from_aws(self):
        aws_queues = self.__get_queues()
        for queue in aws_queues:
            self.queues[queue['jobQueueName']].from_aws(queue)
        aws_compute_environments = self.__get_compute_environments()
        for env in aws_compute_environments:
            self.compute_environments[env['computeEnvironmentName']].from_aws(env)

        for queue in self.queues.values():
            queue.update_compute_environments(aws_compute_environments)

    def create_job_definition(self, name):
        self.job_definitions[name].register()
        # self.describe()

    def update_job_definition(self, name):
        self.job_definitions[name].register()
        # self.describe()

    def deregister_job_definition(self, name):
        self.job_definitions[name].deregister()
        # self.describe()

    def submit_job(self, name, job_description, queue, parameters={}, depends_on=[], overrides={}, retries=0):
        jd = self.job_definitions[job_description]
        jd.register()
        kwargs = {
            'jobDefinition':jd.arn,
            'jobName':name,
            'jobQueue':queue
        }
        if parameters:
            kwargs['parameters'] = parameters
        response = self.batch.submit_job(**kwargs)

    def submit_jobs(self, name, job_description, queue, parameters_csv):
        '''
        Submit Batch Jobs given a CSV file containing rows of parameters
        '''

        jd = self.job_definitions[job_description]
        if not jd.arn:
            jd.register()
        kwargs = {
            'jobDefinition': jd.arn,
            'jobName': name,
            'jobQueue': queue
        }

        with open(parameters_csv, 'rt') as csvfile:
            # first line is parameter names
            parameter_sets = csv.DictReader(csvfile)
            jobs_submitted = 0
            print('Submitting Jobs ', end='')

            for _parameters in parameter_sets:
                self.batch.submit_job(**kwargs)
                jobs_submitted += 1
                if jobs_submitted % 100 == 0:
                    print('.', end='')
                    sys.stdout.flush()

            print('.')
            print('Jobs submitted: {}'.format(jobs_submitted))
            sys.stdout.flush()

    def get_jobs(self, queue):
        jobs = []
        statuses = {
            'SUBMITTED': 0,
            'PENDING': 0,
            'RUNNABLE': 0,
            'STARTING': 0,
            'RUNNING': 0,
            'SUCCEEDED': 0,
            'FAILED': 0
        }

        for status in statuses.keys():
            nextToken = ''
            while True:
                response = self.batch.list_jobs(jobQueue=queue, jobStatus=status, nextToken=nextToken)
                if 'jobSummaryList' in response:
                    joblist = response['jobSummaryList']
                    for job in joblist:
                        jobs.append(job['jobId'])
                        statuses[status] += 1
                nextToken = response.get('nextToken', None)
                if not nextToken:
                    break

        return jobs, statuses

    def list_jobs(self, queue):
        jobs, statuses = self.get_jobs(queue)
        lines = ['Job Status:']
        lines.append("SUB   |PEND  |READY |START |RUN   |FAIL  |SUCCESS ")
        numstr = "{:5d} |{:5d} |{:5d} |{:5d} |{:5d} |{:5d} |{:5d}"
        formstr = numstr.format (
            statuses['SUBMITTED'],
            statuses['PENDING'],
            statuses['RUNNABLE'],
            statuses['STARTING'],
            statuses['RUNNING'],
            statuses['FAILED'],
            statuses['SUCCEEDED'],
        )
        lines.append(formstr)

        runnable_count = 0
        for status in ["SUBMITTED", "PENDING", "RUNNABLE", "STARTING", "RUNNING"]:
            runnable_count += statuses[status]

        # for status in statuses.keys():
        #     lines.append("  {}: {}".format(status, statuses[status]))
        return lines, runnable_count

    def cancel_job(self, job_id, reason):
        self.batch.cancel_job(jobId=job_id, reason=reason)

    def terminate_job(self, job_id, reason):
        self.batch.terminate_job(jobId=job_id, reason=reason)

    def cancel_all_jobs(self, queue):
        reason = "Cancelling all jobs."
        jobs, statuses = self.get_jobs(queue)
        for job in jobs:
            self.cancel_job(job, reason)

    def terminate_all_jobs(self, queue):
        reason = "Terminating all jobs."
        jobs, statuses = self.get_jobs(queue)
        for job in jobs:
            self.terminate_job(job, reason)

    def create_queue(self, queue):
        if queue in self.queues:
            q = self.queues[queue]
            if not q.exists():
                kwargs = q.render()
                response = self.batch.create_job_queue(**kwargs)
            else:
                print("Queue already exists.")

    def update_queue(self, queue):
        if queue in self.queues:
            q = self.queues[queue]
            if q.exists():
                kwargs = q.render(True)
                response = self.batch.update_job_queue(**kwargs)
            else:
                print("Queue must be created first.")

    def disable_queue(self, queue):
        if queue in self.queues:
            q = self.queues[queue]
            if q.exists():
                kwargs = q.render(True)
                kwargs['state'] = 'DISABLED'
                response = self.batch.update_job_queue(**kwargs)
            else:
                print("Queue must be created first.")

    def destroy_queue(self, queue):
        if queue in self.queues:
            q = self.queues[queue]
            if q.exists():
                if q.aws_state() == 'ENABLED':
                    print("Queue must be disabled first.")
                    return
                response = self.batch.delete_job_queue(jobQueue=queue)
            else:
                print("Queue doesn't exist.")

    def create_compute_environment(self, compute_environment):
        if compute_environment in self.compute_environments:
            c = self.compute_environments[compute_environment]
            if not c.exists():
                kwargs = c.render()
                response = self.batch.create_compute_environment(**kwargs)
            else:
                print("Compute Environment already exists.")

    def update_compute_environment(self, compute_environment):
        if compute_environment in self.compute_environments:
            c = self.compute_environments[compute_environment]
            if c.exists():
                kwargs = c.render(True)
                response = self.batch.update_compute_environment(**kwargs)
            else:
                print("Compute Environment must be created first.")

    def disable_compute_environment(self, compute_environment):
        if compute_environment in self.compute_environments:
            c = self.compute_environments[compute_environment]
            if c.exists():
                response = self.batch.update_compute_environment(
                    computeEnvironment=compute_environment,
                    state='DISABLED'
                )
            else:
                print("Compute Environment must be created first.")

    def destroy_compute_environment(self, compute_environment):
        if compute_environment in self.compute_environments:
            c = self.compute_environments[compute_environment]
            if c.exists():
                if c.aws_state() == 'ENABLED':
                    print("Compute environment must be disabled first.")
                response = self.batch.delete_compute_environment(
                    computeEnvironment=compute_environment
                )
            else:
                print("Compute Environment doesn't exist.")

    def indent_description(self, original):
        if not original:
            return []
        description = []
        description.append("  - {}".format(original[0]))
        for desc in original[1:]:
            description.append("    {}".format(desc))
        return description

    def describe(self):
        description = ['Queues:']
        for name, queue in self.queues.items():
            description.extend(self.indent_description(queue.describe()))
        description.append('')
        description.append('Compute Environments:')
        for name, env in self.compute_environments.items():
            description.extend(self.indent_description(env.describe()))
        return description
        description.append('')
        description.append('Job Definitions:')
        for name, jd in self.job_definitions.items():
            description.extend(self.indent_description(jd.describe()))
        return description

    def assemble(self):

        # compute environments
        print('Creating Compute Environments')
        compute_environments = set(self.compute_environments.keys())
        for compute_environment in compute_environments:
            c = self.compute_environments[compute_environment]
            if not c.exists():
                self.create_compute_environment(compute_environment)
            else:
                self.update_compute_environment(compute_environment)

        while True:
            time.sleep(3)
            if compute_environments.issubset([
                env_dict['computeEnvironmentName']
                for env_dict in self.__get_compute_environments()
                if env_dict['status'] == 'VALID'
            ]):
                break

        self.from_aws()

        # queues
        print('Creating Job Queues')
        queues = set(self.queues.keys())
        for queue in queues:
            q = self.queues[queue]
            if not q.exists():
                self.create_queue(queue)
            else:
                self.update_queue(queue)

        self.from_aws()

        # job definitions
        print('Creating Job Definitions')
        for job_definition in self.job_definitions.keys():
            self.create_job_definition(job_definition)

        print('Assembly complete')

    def teardown(self):

        # job definitions
        print('Deleting Job Definitions')
        for job_definition in self.job_definitions.keys():
            self.deregister_job_definition(job_definition)

        # job queues
        print('Deleting Job Queues')
        queues = list(self.queues.keys())
        for queue in queues:
            self.terminate_all_jobs(queue)

        for queue_dict in self.__get_queues():
            if queue_dict['state'] != 'DISABLED':
                self.disable_queue(queue_dict['jobQueueName'])

        enabled = [True]
        while any(enabled):
            time.sleep(3)
            enabled = []
            for queue_dict in self.__get_queues():
                enabled.append(queue_dict['state'] != 'DISABLED' or queue_dict['status'] == 'UPDATING')

        self.from_aws()

        for queue_dict in self.__get_queues():
            if queue_dict['status'] not in ('DELETED', 'DELETING'):
                self.destroy_queue(queue_dict['jobQueueName'])

        exists = [True]
        while any(exists):
            time.sleep(3)
            exists = []
            for queue_dict in self.__get_queues():
                exists.append(queue_dict['status'] != 'DELETED')

        self.from_aws()

        # compute environments
        print('Deleting Compute Environments')
        for env_dict in self.__get_compute_environments():
            if env_dict['state'] != 'DISABLED':
                self.disable_compute_environment(env_dict['computeEnvironmentName'])

        enabled = [True]
        while any(enabled):
            time.sleep(3)
            enabled = []
            for env_dict in self.__get_compute_environments():
                enabled.append(env_dict['state'] != 'DISABLED' or env_dict['status'] == 'UPDATING')

        self.from_aws()

        for compute_environment in self.compute_environments.keys():
            self.destroy_compute_environment(compute_environment)

        exists = [True]
        while any(exists):
            time.sleep(3)
            exists = []
            for env_dict in self.__get_compute_environments():
                exists.append(env_dict['status'] != 'DELETED')

        print('Teardown complete')
