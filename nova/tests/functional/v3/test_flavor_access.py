# Copyright 2013 IBM Corp.
#
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

from oslo_config import cfg

from nova.tests.functional.v3 import api_sample_base

CONF = cfg.CONF
CONF.import_opt('osapi_compute_extension',
                'nova.api.openstack.compute.legacy_v2.extensions')


class FlavorAccessSampleJsonTests(api_sample_base.ApiSampleTestBaseV3):
    ADMIN_API = True
    extension_name = 'flavor-access'
    # TODO(Park): Overriding '_api_version' till all functional tests
    # are merged between v2 and v2.1. After that base class variable
    # itself can be changed to 'v2'
    _api_version = 'v2'

    def _get_flags(self):
        f = super(FlavorAccessSampleJsonTests, self)._get_flags()
        f['osapi_compute_extension'] = CONF.osapi_compute_extension[:]
        f['osapi_compute_extension'].append(
                    'nova.api.openstack.compute.contrib.'
                    'flavor_access.Flavor_access')
        # FlavorAccess extension also needs Flavormanage to be loaded.
        f['osapi_compute_extension'].append(
                    'nova.api.openstack.compute.contrib.'
                    'flavormanage.Flavormanage')
        f['osapi_compute_extension'].append(
                    'nova.api.openstack.compute.contrib.'
                    'flavor_disabled.Flavor_disabled')
        f['osapi_compute_extension'].append(
                    'nova.api.openstack.compute.contrib.'
                    'flavorextradata.Flavorextradata')
        f['osapi_compute_extension'].append(
                    'nova.api.openstack.compute.contrib.'
                    'flavor_swap.Flavor_swap')
        return f

    def _add_tenant(self):
        subs = {
            'tenant_id': 'fake_tenant',
            'flavor_id': 10,
        }
        response = self._do_post('flavors/10/action',
                                 'flavor-access-add-tenant-req',
                                 subs)
        self._verify_response('flavor-access-add-tenant-resp',
                              subs, response, 200)

    def _create_flavor(self):
        subs = {
            'flavor_id': 10,
            'flavor_name': 'test_flavor'
        }
        response = self._do_post("flavors",
                                 "flavor-access-create-req",
                                 subs)
        subs.update(self._get_regexes())
        self._verify_response("flavor-access-create-resp", subs, response, 200)

    def test_flavor_access_create(self):
        self._create_flavor()

    def test_flavor_access_detail(self):
        response = self._do_get('flavors/detail')
        subs = self._get_regexes()
        self._verify_response('flavor-access-detail-resp', subs, response, 200)

    def test_flavor_access_list(self):
        self._create_flavor()
        self._add_tenant()
        flavor_id = 10
        response = self._do_get('flavors/%s/os-flavor-access' % flavor_id)
        subs = {
            'flavor_id': flavor_id,
            'tenant_id': 'fake_tenant',
        }
        self._verify_response('flavor-access-list-resp', subs, response, 200)

    def test_flavor_access_show(self):
        flavor_id = 1
        response = self._do_get('flavors/%s' % flavor_id)
        subs = {
            'flavor_id': flavor_id
        }
        subs.update(self._get_regexes())
        self._verify_response('flavor-access-show-resp', subs, response, 200)

    def test_flavor_access_add_tenant(self):
        self._create_flavor()
        self._add_tenant()

    def test_flavor_access_remove_tenant(self):
        self._create_flavor()
        self._add_tenant()
        subs = {
            'tenant_id': 'fake_tenant',
        }
        response = self._do_post('flavors/10/action',
                                 "flavor-access-remove-tenant-req",
                                 subs)
        exp_subs = {
            "tenant_id": self.api.project_id,
            "flavor_id": "10"
        }
        self._verify_response('flavor-access-remove-tenant-resp',
                              exp_subs, response, 200)
