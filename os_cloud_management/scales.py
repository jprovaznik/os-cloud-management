# Copyright 2015 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import logging
import time

LOG = logging.getLogger(__name__)


class ScaleManager:
    def __init__(self, tuskarclient, heatclient, plan_id=None, stack_id=None):
        self.tuskarclient = tuskarclient
        self.heatclient = heatclient
        self.stack_id = stack_id
        self.plan_id = plan_id

    def scaleup(self, role, num):
        # TODO(jprovazn): update plan in tuskar
        #plan = tuskarutils.find_resource(self.tuskarclient.plans, 'overcloud')
        #plan = self.tuskarclient.plans.get(plan_uuid=self.plan_id)
        param_name = "{0}::count".format(role)
        plan = self.tuskarclient.plans.patch(
            self.plan_id, [{'name': '{0}::count'.format(role),
                            'value': num}])
        templates = self.tuskarclient.plans.templates(self.plan_id)
        master = templates.get('plan.yaml')
        env = templates.get('environment.yaml')
        del templates['plan.yaml']
        del templates['environment.yaml']

        # TODO: add breakpoints
        params = {
            'template': master,
            'environment': env,
            'files': templates,
        }
        stack = self.heatclient.stacks.update(self.stack_id, **params)
