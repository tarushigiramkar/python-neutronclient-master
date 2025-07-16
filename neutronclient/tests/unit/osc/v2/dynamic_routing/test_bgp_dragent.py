#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
from unittest import mock

from neutronclient.osc.v2.dynamic_routing import bgp_dragent
from neutronclient.tests.unit.osc.v2.dynamic_routing import fakes


class TestAddBgpSpeakerToDRAgent(fakes.TestNeutronDynamicRoutingOSCV2):
    _bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
    _bgp_dragent = fakes.FakeDRAgent.create_one_dragent()
    _bgp_speaker_id = _bgp_speaker['id']
    _bgp_dragent_id = _bgp_dragent['id']

    def setUp(self):
        super(TestAddBgpSpeakerToDRAgent, self).setUp()

       
        self.cmd = bgp_dragent.AddBgpSpeakerToDRAgent(self.app, self.namespace)

    def test_add_bgp_speaker_to_dragent(self):
        arglist = [
            self._bgp_dragent_id,
            self._bgp_speaker_id,
        ]
        verifylist = [
            ('dragent_id', self._bgp_dragent_id),
            ('bgp_speaker', self._bgp_speaker_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(self.networkclient,
                               "add_bgp_speaker_to_dragent",
                               return_value=None):

            result = self.cmd.take_action(parsed_args)

           
            self.networkclient.add_bgp_speaker_to_dragent.\
                assert_called_once_with(
                    self._bgp_speaker_id, self._bgp_dragent_id)

            self.assertIsNone(result)




class TestRemoveBgpSpeakerFromDRAgent(fakes.TestNeutronDynamicRoutingOSCV2):
    _bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
    _bgp_dragent = fakes.FakeDRAgent.create_one_dragent()
    _bgp_speaker_id = _bgp_speaker['id']
    _bgp_dragent_id = _bgp_dragent['id']

    def setUp(self):
        super(TestRemoveBgpSpeakerFromDRAgent, self).setUp()

        # Get the command object to test
        self.cmd = bgp_dragent.RemoveBgpSpeakerFromDRAgent(
            self.app, self.namespace)

    def test_remove_bgp_speaker_from_dragent(self):
        arglist = [
            self._bgp_dragent_id,
            self._bgp_speaker_id,
        ]
        verifylist = [
            ('dragent_id', self._bgp_dragent_id),
            ('bgp_speaker', self._bgp_speaker_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(self.networkclient,
                               "remove_bgp_speaker_from_dragent",
                               return_value=None):
            result = self.cmd.take_action(parsed_args)

           
            self.networkclient.remove_bgp_speaker_from_dragent.\
                assert_called_once_with(self._bgp_speaker_id,
                                        self._bgp_dragent_id)

            self.assertIsNone(result)


class TestListDRAgentsHostingBgpSpeaker(fakes.TestNeutronDynamicRoutingOSCV2):
    
    def setUp(self):
        super(TestListDRAgentsHostingBgpSpeaker, self).setUp()
        
        # Get the command object to test
        self.cmd = bgp_dragent.ListDRAgent(self.app, self.namespace)
        
        # Create fake BGP speaker and DR agents  
        self._bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
        self._bgp_speaker_id = self._bgp_speaker['id']
        
        # Create multiple fake DR agents with realistic data
        self._dragents = fakes.FakeDRAgent.create_dragents(count=3)
        
        # Convert to dict format as returned by the API
        self._dragents_data = []
        for agent in self._dragents:
            agent_dict = {
                'id': agent.id,
                'agent_type': agent.agent_type,
                'host': agent.host,
                'availability_zone': agent.availability_zone,
                'is_alive': agent.alive,
                'is_admin_state_up': agent.admin_state_up,
                'binary': agent.binary
            }
            self._dragents_data.append(agent_dict)

    def test_list_dragents_hosting_bgp_speaker(self):
        arglist = [
            '--bgp-speaker', self._bgp_speaker_id,
        ]
        verifylist = [
            ('bgp_speaker', self._bgp_speaker_id),
        ]
        
        # Parse the arguments
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        
        # Mock the network client methods
        self.networkclient.find_bgp_speaker.return_value = self._bgp_speaker
        self.networkclient.get_bgp_dragents_hosting_speaker.return_value = \
            self._dragents_data
        
        # Execute the command
        columns, data = self.cmd.take_action(parsed_args)
        
        # Verify the BGP speaker was looked up correctly
        self.networkclient.find_bgp_speaker.assert_called_once_with(
            self._bgp_speaker_id
        )
        
        # Verify the correct API method was called with the speaker ID
        self.networkclient.get_bgp_dragents_hosting_speaker.assert_called_once_with(
            self._bgp_speaker_id
        )
        
        # Verify the column headers are correct
        expected_columns = (
            'ID',
            'Agent Type', 
            'Host',
            'Availability Zone',
            'Alive',
            'State',
            'Binary'
        )
        self.assertEqual(expected_columns, columns)
        
        # Verify the data is formatted correctly
        # Convert generator to list for comparison
        data_list = list(data)
        self.assertEqual(len(self._dragents_data), len(data_list))
        
        # Check each row of data
        for i, row in enumerate(data_list):
            agent = self._dragents_data[i]
            expected_row = (
                agent['id'],
                agent['agent_type'],
                agent['host'],
                agent['availability_zone'],
                agent['is_alive'],
                agent['is_admin_state_up'],
                agent['binary']
            )
            self.assertEqual(expected_row, row)
