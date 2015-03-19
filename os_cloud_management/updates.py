import json
import logging
import time

from heatclient.client import Client

LOG = logging.getLogger(__name__)


class UpdateManager:
    def __init__(self, client, stack_id=None):
        self.client = client
        self.stack_id = stack_id


    def start(self, orig_stack_id, template_name, update_name=None):
        orig_stack = self.client.stacks.get(orig_stack_id)
        if not update_name:
            update_name = '{name}_update'.format(name=orig_stack.stack_name)
        servers = {}
        breakpoints = []
        for x in self.client.resources.list(orig_stack_id, 2):
            if x.resource_type == 'OS::Nova::Server':
                sid = '{lresource}-{parent}'.format(
                        lresource = x.logical_resource_id,
                        parent=x.parent_resource)
                servers[sid] = x.physical_resource_id
        with open(template_name, 'r') as f:
            template = f.read()
        env = {
            'resource_registry': {
                'resources': {
                    'deployments': {
                        '*': {'hooks': 'pre-create' }
                    }
                }
            }
        }
        params = {
            'stack_name': update_name,
            'template': template,
            'environment': env,
            'parameters': {'servers': json.dumps(servers)}}
        #server_ids = get_list_of_server_ids
        #sw_config = get_sw_config_update_resource
        #stack = heat.create_nested_stack_with_breakpoints(ids - 1, sw_config)
        #return stack
        LOG.debug('creating stack: {0}', params)
        stack = self.client.stacks.create(**params)
        self.stack_id = stack['stack']['id']
        return self.stack_id


    def proceed(self, node=None):
        stack = self.client.stacks.get(self.stack_id)
        resources = self._resources_by_state()
        try:
            self._clear_breakpoint(resources['on_breakpoint'].pop())
        except IndexError:
            print "no more breakpoints"


    def cancel(stack):
        # TODO
        stack.rollback
        stack.delete


    def get_status(self, verbose=False):
        stack = self.client.stacks.get(self.stack_id)
        # check if any of deployments' child resource has last
        # event indicating that it has reached a breakpoint (this
        # seems to be the only way how to check pre-create breakpoints ATM)
        resources = self._resources_by_state()
        if stack.status == 'IN_PROGRESS':
            if verbose:
                print resources
            if resources['on_breakpoint']:
                if resources['in_progress']:
                    status = 'IN_PROGRESS'
                else:
                    status = 'WAITING'
            else:
                status = 'IN_PROGRESS'
        else:
            status = stack.status
        LOG.debug('%s status: %s', stack.stack_name, status)
        return (status, resources)


    def do_interactive_update(self):
        status = None
        while status not in ['COMPLETE', 'FAILED']:
            status, resources = self.get_status()
            if status == 'WAITING':
                print resources
                user_input = raw_input("Breakpoint reached, continue? Press "
                                       "Enter or C-c:")
                self.proceed()
            time.sleep(1)
        print 'update finished with status {0}'.format(status)


    def _clear_breakpoint(self, node_name):
        LOG.debug('clearing breakpoint on %s' % node_name)
        deployment_resource = self.client.resources.get(
                self.stack_id, 'deployments')
        self.client.resources.signal(
                stack_id=deployment_resource.physical_resource_id,
                resource_name=node_name,
                data={'unset_hook': 'pre-create'})

    def _resources_by_state(self):
        resources = {
            'in_progress': [],
            'on_breakpoint': [],
            'completed': [],
        }
        # FIXME: check only CRATE_* states for now
        for ev in self._last_events().items():
            if ev[1].resource_status == 'CREATE_IN_PROGRESS':
                if ev[1].resource_status_reason != 'Paused until the hook is cleared':
                    resources['in_progress'].append(ev[0])
                else:
                    resources['on_breakpoint'].append(ev[0])
            else:
                resources['completed'].append(ev[0])
        return resources


    def _last_events(self):
        deployment_resource = self.client.resources.get(
                self.stack_id, 'deployments')
        # 'deployments' resource may not exist right after update
        # stack is created
        if not deployment_resource.physical_resource_id:
            return {}
        last_events = {}
        for ev in self.client.events.list(
                deployment_resource.physical_resource_id):
            last_known_ev = last_events.get(ev.resource_name, None)
            # FIXME: proper datetime comparison
            if not last_known_ev or ev.event_time > last_known_ev.event_time:
                last_events[ev.resource_name] = ev
        return last_events
