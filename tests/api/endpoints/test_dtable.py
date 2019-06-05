# -*- coding: utf-8 -*-
import json

from django.core.urlresolvers import reverse

from seaserv import seafile_api

from seahub.dtable.models import Workspaces
from seahub.test_utils import BaseTestCase


class WorkspacesViewTest(BaseTestCase):

    def setUp(self):
        workspace = Workspaces.objects.create_workspace("name1", self.user.username, self.repo.id)
        self.url = reverse('api-v2.1-workspaces')
        self.login_as(self.user)

    def test_can_list(self):
        assert len(Workspaces.objects.all()) == 1

        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)

        json_resp = json.loads(resp.content)
        self.assertIsNotNone(json_resp["workspace_list"])

    def test_list_with_invalid_repo(self):
        assert len(Workspaces.objects.all()) == 1

        url = reverse('api2-repo', args=[self.repo.id])
        resp = self.client.delete(url, {}, 'application/x-www-form-urlencoded')
        self.assertEqual(200, resp.status_code)

        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)

        json_resp = json.loads(resp.content)
        assert json_resp["workspace_list"] == []

    def test_can_create(self):
        assert len(Workspaces.objects.all()) == 1

        resp = self.client.post(self.url, {'name': 'name2'})
        self.assertEqual(201, resp.status_code)

        assert len(Workspaces.objects.all()) == 2

        json_resp = json.loads(resp.content)
        assert json_resp["workspace"]["name"] == 'name2'


class WorkspaceViewTest(BaseTestCase):

    def setUp(self):
        self.workspace = Workspaces.objects.create_workspace("name1", self.user.username, self.repo.id)
        self.url = reverse('api-v2.1-workspace', args=[self.workspace.id])
        self.login_as(self.user)

    def test_can_rename(self):
        data = 'name=%s' % 'name2'
        resp = self.client.put(self.url, data, 'application/x-www-form-urlencoded')
        self.assertEqual(200, resp.status_code)

        json_resp = json.loads(resp.content)
        assert json_resp["workspace"]["name"] == 'name2'

    def test_rename_with_invalid_permission(self):
        self.logout()
        self.login_as(self.admin)

        data = 'name=%s' % 'name2'
        resp = self.client.put(self.url, data, 'application/x-www-form-urlencoded')
        self.assertEqual(403, resp.status_code)

    def test_rename_with_invalid_repo(self):
        url = reverse('api2-repo', args=[self.workspace.repo_id])
        resp = self.client.delete(url, {}, 'application/x-www-form-urlencoded')
        self.assertEqual(200, resp.status_code)

        data = 'name=%s' % 'name2'
        resp = self.client.put(self.url, data, 'application/x-www-form-urlencoded')
        self.assertEqual(404, resp.status_code)

    def test_can_delete(self):
        assert len(Workspaces.objects.all()) == 1

        resp = self.client.delete(self.url, {'name': 'name1'})
        self.assertEqual(200, resp.status_code)

        assert len(Workspaces.objects.all()) == 0

    def test_delete_with_invalid_permission(self):
        self.logout()
        self.login_as(self.admin)

        resp = self.client.delete(self.url, {'name': 'name1'})
        self.assertEqual(403, resp.status_code)


class DTableTest(BaseTestCase):

    def setUp(self):
        self.workspace = Workspaces.objects.create_workspace("workspace", self.user.username, self.repo.id)
        self.url = reverse('api-v2.1-workspace-dtable', args=[self.workspace.id])
        self.login_as(self.user)

    def test_can_create(self):
        resp = self.client.post(self.url, {'name': 'table1'})
        self.assertEqual(201, resp.status_code)

        json_resp = json.loads(resp.content)
        assert json_resp["table"]["name"] == 'table1'

    def test_create_with_invalid_repo(self):
        url = reverse('api2-repo', args=[self.workspace.repo_id])
        resp = self.client.delete(url, {}, 'application/x-www-form-urlencoded')
        self.assertEqual(200, resp.status_code)

        resp = self.client.post(self.url, {'name': 'table1'})
        self.assertEqual(404, resp.status_code)

    def test_can_rename(self):
        resp = self.client.post(self.url, {'name': 'table4'})
        self.assertEqual(201, resp.status_code)

        json_resp = json.loads(resp.content)
        assert json_resp["table"]["name"] == 'table4'

        old_name = json_resp["table"]["name"]
        new_name = 'table5'

        resp = self.client.put(
            self.url,
            'old_name=table4&new_name=table5',
            'application/x-www-form-urlencoded'
        )

        self.assertEqual(200, resp.status_code)

        json_resp = json.loads(resp.content)
        assert json_resp["table"]["name"] == 'table5'

    def test_rename_with_invalid_workspace(self):
        resp = self.client.post(self.url, {'name': 'table6'})
        self.assertEqual(201, resp.status_code)

        json_resp = json.loads(resp.content)
        assert json_resp["table"]["name"] == 'table6'

        url = reverse('api-v2.1-workspace', args=[self.workspace.id])
        resp = self.client.delete(url, {'name': 'workspace'})

        self.assertEqual(200, resp.status_code)

        resp = self.client.put(
            self.url,
            'old_name=table6&new_name=table7',
            'application/x-www-form-urlencoded'
        )

        self.assertEqual(404, resp.status_code)

    def test_can_delete(self):
        resp = self.client.post(self.url, {'name': 'table1'})
        self.assertEqual(201, resp.status_code)

        json_resp = json.loads(resp.content)
        assert json_resp["table"]["name"] == 'table1'

        data = 'name=%s' % 'table1'
        resp = self.client.delete(self.url, data, 'application/x-www-form-urlencoded')
        self.assertEqual(200, resp.status_code)

    def test_delete_with_invalid_permission(self):
        resp = self.client.post(self.url, {'name': 'table2'})
        self.assertEqual(201, resp.status_code)

        json_resp = json.loads(resp.content)
        assert json_resp["table"]["name"] == 'table2'

        self.logout()
        self.login_as(self.admin)

        data = 'name=%s' % 'table2'
        resp = self.client.delete(self.url, data, 'application/x-www-form-urlencoded')
        self.assertEqual(403, resp.status_code)

    def test_delete_with_repo_only_read(self):
        resp = self.client.post(self.url, {'name': 'table3'})
        self.assertEqual(201, resp.status_code)

        json_resp = json.loads(resp.content)
        assert json_resp["table"]["name"] == 'table3'

        seafile_api.set_repo_status(self.workspace.repo_id, 1)

        data = 'name=%s' % 'table3'
        resp = self.client.delete(self.url, data, 'application/x-www-form-urlencoded')
        self.assertEqual(403, resp.status_code)