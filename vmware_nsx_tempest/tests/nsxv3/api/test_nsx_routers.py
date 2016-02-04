# Copyright 2016 VMware Inc
# All Rights Reserved
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

from tempest.api.network import base_routers as base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test

from vmware_nsx_tempest.services import nsxv3_client

CONF = config.CONF


class NSXv3RoutersTest(base.BaseRouterTest):

    @classmethod
    def skip_checks(cls):
        super(NSXv3RoutersTest, cls).skip_checks()
        if not test.is_extension_enabled('router', 'network'):
            msg = "router extension not enabled."
            raise cls.skipException(msg)

    @classmethod
    def resource_setup(cls):
        super(NSXv3RoutersTest, cls).resource_setup()
        cls.nsx = nsxv3_client.NSXV3Client(CONF.nsxv3.nsx_manager,
                                           CONF.nsxv3.nsx_user,
                                           CONF.nsxv3.nsx_password)

    @test.attr(type='nsxv3')
    @test.idempotent_id('0e9938bc-d2a3-4a9a-a4f9-7a93ee8bb344')
    def test_create_update_delete_nsx_router(self):
        # Create a router
        name = data_utils.rand_name('router-')
        router = self.create_router(name, admin_state_up=True)
        self.addCleanup(self._delete_router, router['id'])
        nsx_router = self.nsx.get_logical_router(router['name'],
                                                 router['id'])
        self.assertEqual(router['name'], name)
        self.assertEqual(router['admin_state_up'], True)
        self.assertIsNotNone(nsx_router)
        # Update the name of router and verify if it is updated on both
        # neutron and nsx backend
        updated_name = 'updated ' + name
        update_body = self.client.update_router(router['id'],
                                                name=updated_name)
        updated_router = update_body['router']
        nsx_router = self.nsx.get_logical_router(updated_router['name'],
                                                 updated_router['id'])
        self.assertEqual(updated_router['name'], updated_name)
        self.assertIsNotNone(nsx_router)
        # Delete the router and verify it is deleted on nsx backend
        self.client.delete_router(updated_router['id'])
        nsx_router = self.nsx.get_logical_router(updated_router['name'],
                                                 updated_router['id'])
        self.assertIsNone(nsx_router)

    def _delete_router(self, router_id):
        # Delete the router in case the test exits with any exception
        list_body = self.client.list_routers()
        for router in list_body['router']:
            if router['id'] == router_id:
                self.client.delete_router(router_id)
