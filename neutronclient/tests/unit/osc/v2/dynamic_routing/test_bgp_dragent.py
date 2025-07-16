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
    _bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
    _bgp_speaker_id = _bgp_speaker['id']
    _dragents = fakes.FakeDRAgent.create_dragents(count=3)

    def setUp(self):
        super(TestListDRAgentsHostingBgpSpeaker, self).setUp()
        # Set up the command object to test
        self.cmd = bgp_dragent.ListDRAgent(self.app, self.namespace)

    def test_list_dragents_hosting_bgp_speaker(self):
        arglist = [
            '--bgp-speaker', self._bgp_speaker_id,
        ]
        verifylist = [
            ('bgp_speaker', self._bgp_speaker_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Set the return value of get_bgp_dragents_hosting_speaker
        self.networkclient.get_bgp_dragents_hosting_speaker = mock.Mock(
            return_value=self._dragents)

        # Execute the command
        columns, data = self.cmd.take_action(parsed_args)

        # Verify the API call
        self.networkclient.get_bgp_dragents_hosting_speaker.assert_called_once_with(
            self._bgp_speaker_id)
        
        # Check that columns are correct
        self.assertEqual(
            ('ID', 'Agent Type', 'Host', 'Availability Zone', 'Alive', 'State', 'Binary'),
            columns)

        # Check that the data matches our mocked dynamic routing agents
        agents_data = list(data)
        self.assertEqual(len(agents_data), 3)  # We created 3 agents in our mock
        
        for i, agent in enumerate(agents_data):
            self.assertEqual(agent[0], self._dragents[i].id)  # ID
            self.assertEqual(agent[1], self._dragents[i].agent_type)  # Agent Type
            self.assertEqual(agent[2], self._dragents[i].host)  # Host
            self.assertEqual(agent[3], self._dragents[i].availability_zone)  # Availability Zone
            self.assertEqual(agent[4], self._dragents[i].is_alive)  # Alive
            self.assertEqual(agent[5], self._dragents[i].is_admin_state_up)  # State
            self.assertEqual(agent[6], self._dragents[i].binary)  # Binary


class TestListDRAgents(fakes.TestNeutronDynamicRoutingOSCV2):
    _dragents = fakes.FakeDRAgent.create_dragents(count=3)

    def setUp(self):
        super(TestListDRAgents, self).setUp()
        # Set up the command object to test
        self.cmd = bgp_dragent.ListDRAgent(self.app, self.namespace)

    def test_list_all_dragents(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Set the return value of agents
        self.networkclient.agents = mock.Mock(return_value=self._dragents)

        # Execute the command
        columns, data = self.cmd.take_action(parsed_args)

        # Verify the API call
        self.networkclient.agents.assert_called_once_with(
            agent_type='BGP dynamic routing agent')
        
        # Check that columns are correct
        self.assertEqual(
            ('ID', 'Agent Type', 'Host', 'Availability Zone', 'Alive', 'State', 'Binary'),
            columns)

        # Check that the data matches our mocked dynamic routing agents
        agents_data = list(data)
        self.assertEqual(len(agents_data), 3)  # We created 3 agents in our mock
        
        for i, agent in enumerate(agents_data):
            self.assertEqual(agent[0], self._dragents[i].id)  # ID
            self.assertEqual(agent[1], self._dragents[i].agent_type)  # Agent Type
            self.assertEqual(agent[2], self._dragents[i].host)  # Host
            self.assertEqual(agent[3], self._dragents[i].availability_zone)  # Availability Zone
            self.assertEqual(agent[4], self._dragents[i].is_alive)  # Alive
            self.assertEqual(agent[5], self._dragents[i].is_admin_state_up)  # State
            self.assertEqual(agent[6], self._dragents[i].binary)  # Binary
