# Copyright 2015 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import mock
import testtools

from os_cloud_management import updates
from os_cloud_management.tests import base

class UpdateManagerTest(base.TestCase):

    def setUp(self):
        super(UpdateManagerTest, self).setUp()
        self.image = collections.namedtuple('image', ['id'])

    def test_start_update(self):
        client = mock.MagicMock()
        client.stacks.get.return_value = mock.MagicMock(stack_name='stack')
        mock_resource = mock.MagicMock(
            resource_type='OS::Nova::Server', logical_resource_id='logical_id',
            physical_resource_id='physical_id', parent_resource='parent')
        client.resources.list.return_value = [mock_resource]
        with mock.patch('os_cloud_management.updates.open',
                        mock.mock_open(read_data='template body'),
                        create=True) as mopen:
            updates.UpdateManager(client).start('123', 'template.yaml')
        env = {
            'resource_registry': {
                'resources': {
                    'deployments': {
                        '*': {'hooks': 'pre-create'}
                    }
                }
            }
        }
        params = {
            'stack_name': 'stack_update',
            'template': 'template body',
            'environment': {
                'resource_registry': {
                    'resources': {
                        'deployments': {
                            '*': {'hooks': 'pre-create'}
                        }
                    }
                }
            },
            'parameters': {'servers': '{"logical_id-parent": "physical_id"}'}}
        client.stacks.get.assert_called_once_with('123')
        client.resources.list.assert_called_once_with('123', 2)
        client.stacks.create.assert_called_once_with(**params)
