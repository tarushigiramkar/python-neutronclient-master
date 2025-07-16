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
    """Test case for AddBgpSpeakerToDRAgent command."""
    
    def setUp(self):
        super(TestAddBgpSpeakerToDRAgent, self).setUp()
        self._bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
        self._bgp_dragent = fakes.FakeDRAgent.create_one_dragent()
        self._bgp_speaker_id = self._bgp_speaker['id']
        self._bgp_dragent_id = self._bgp_dragent['id']
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
                    self._bgp_dragent_id, self._bgp_speaker_id)
            self.assertIsNone(result)


class TestRemoveBgpSpeakerFromDRAgent(fakes.TestNeutronDynamicRoutingOSCV2):
    """Test case for RemoveBgpSpeakerFromDRAgent command."""
    
    def setUp(self):
        super(TestRemoveBgpSpeakerFromDRAgent, self).setUp()
        self._bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
        self._bgp_dragent = fakes.FakeDRAgent.create_one_dragent()
        self._bgp_speaker_id = self._bgp_speaker['id']
        self._bgp_dragent_id = self._bgp_dragent['id']
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
                assert_called_once_with(self._bgp_dragent_id,
                                        self._bgp_speaker_id)
            self.assertIsNone(result)


class TestListDRAgentsHostingBgpSpeaker(fakes.TestNeutronDynamicRoutingOSCV2):
    """Test case for ListDRAgent command when filtering by BGP speaker."""
    
    def setUp(self):
        super(TestListDRAgentsHostingBgpSpeaker, self).setUp()
        self._bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
        self._bgp_speaker_id = self._bgp_speaker['id']
        self._dragents = fakes.FakeDRAgent.create_dragents(count=3)
        self.cmd = bgp_dragent.ListDRAgent(self.app, self.namespace)

    def test_list_dragents_hosting_bgp_speaker(self):
        """Test list_dragents with bgp-speaker filter."""
        # Command arguments
        arglist = [
            '--bgp-speaker', self._bgp_speaker_id,
        ]
        verifylist = [
            ('bgp_speaker', self._bgp_speaker_id),
        ]
        
        # Parse arguments
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Mock the API call and execute the command
        with mock.patch.object(self.networkclient,
                             "get_bgp_dragents_hosting_speaker",
                             return_value=self._dragents) as mock_list:
            columns, data = self.cmd.take_action(parsed_args)
            
            # Verify API call was made with correct parameters
            mock_list.assert_called_once_with(self._bgp_speaker_id)
            
            # Check that columns are correct
            expected_columns = (
                'ID', 'Agent Type', 'Host', 'Availability Zone', 
                'Alive', 'State', 'Binary'
            )
            self.assertEqual(expected_columns, columns)
            
            # Convert generator to list for testing
            data_list = list(data)
            self.assertEqual(len(data_list), 3)
            
            # Check each row of data
            for i, agent_data in enumerate(data_list):
                agent = self._dragents[i]
                self.assertEqual(agent.id, agent_data[0])  # ID
                self.assertEqual(agent.agent_type, agent_data[1])  # Agent Type
                self.assertEqual(agent.host, agent_data[2])  # Host
                self.assertEqual(agent.availability_zone, agent_data[3])  # AZ
                self.assertEqual(agent.is_alive, agent_data[4])  # Alive
                self.assertEqual(agent.is_admin_state_up, agent_data[5])  # State
                self.assertEqual(agent.binary, agent_data[6])  # Binary

    def test_list_dragents_without_bgp_speaker(self):
        """Test list_dragents without a bgp-speaker filter."""
        # Command arguments (empty)
        arglist = []
        verifylist = []
        
        # Parse arguments
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Mock the API call and execute the command
        with mock.patch.object(self.networkclient,
                              "agents",
                              return_value=self._dragents) as mock_list:
            columns, data = self.cmd.take_action(parsed_args)
            
            # Verify API call was made with correct parameters
            mock_list.assert_called_once_with(agent_type='BGP dynamic routing agent')
            
            # Check that columns are correct
            expected_columns = (
                'ID', 'Agent Type', 'Host', 'Availability Zone', 
                'Alive', 'State', 'Binary'
            )
            self.assertEqual(expected_columns, columns)
            
            # Convert generator to list for testing
            data_list = list(data)
            self.assertEqual(len(data_list), 3)
            
            # Check each row of data
            for i, agent_data in enumerate(data_list):
                agent = self._dragents[i]
                self.assertEqual(agent.id, agent_data[0])  # ID
                self.assertEqual(agent.agent_type, agent_data[1])  # Agent Type
                self.assertEqual(agent.host, agent_data[2])  # Host
                self.assertEqual(agent.availability_zone, agent_data[3])  # AZ
                self.assertEqual(agent.is_alive, agent_data[4])  # Alive
                self.assertEqual(agent.is_admin_state_up, agent_data[5])  # State
                self.assertEqual(agent.binary, agent_data[6])  # Binary
