from __future__ import absolute_import

import uuid

from django.urls import reverse
from le_utils.constants import content_kinds
from le_utils.constants import file_formats
from le_utils.constants import format_presets

from contentcuration import models
from contentcuration.tests import testdata
from contentcuration.tests.base import StudioAPITestCase
from contentcuration.tests.viewsets.base import generate_create_event
from contentcuration.tests.viewsets.base import generate_delete_event
from contentcuration.tests.viewsets.base import generate_update_event
from contentcuration.tests.viewsets.base import SyncTestMixin
from contentcuration.viewsets.sync.constants import FILE


class SyncTestCase(SyncTestMixin, StudioAPITestCase):

    @property
    def file_metadata(self):
        return {
            "id": uuid.uuid4().hex,
            "contentnode": self.channel.main_tree.get_descendants().first().id,
            "checksum": uuid.uuid4().hex,
            "preset": format_presets.AUDIO,
            "file_format": file_formats.MP3,
            "uploaded_by": self.user.id,
        }

    @property
    def file_db_metadata(self):
        return {
            "id": uuid.uuid4().hex,
            "contentnode_id": self.channel.main_tree.get_descendants().first().id,
            "checksum": uuid.uuid4().hex,
            "preset_id": format_presets.AUDIO,
            "file_format_id": file_formats.MP3,
            "uploaded_by": self.user,
        }

    def setUp(self):
        super(SyncTestCase, self).setUp()
        self.channel = testdata.channel()
        self.user = testdata.user()
        self.channel.editors.add(self.user)
        self.client.force_authenticate(user=self.user)

    def test_cannot_create_file(self):
        file = self.file_metadata
        response = self.sync_changes(
            [generate_create_event(file["id"], FILE, file, channel_id=self.channel.id)],
        )
        self.assertEqual(len(response.data["errors"]), 1)
        try:
            models.File.objects.get(id=file["id"])
            self.fail("File was created")
        except models.File.DoesNotExist:
            pass

    def test_cannot_create_files(self):
        file1 = self.file_metadata
        file2 = self.file_metadata
        response = self.sync_changes(
            [
                generate_create_event(file1["id"], FILE, file1, channel_id=self.channel.id),
                generate_create_event(file2["id"], FILE, file2, channel_id=self.channel.id),
            ],
        )
        self.assertEqual(len(response.data["errors"]), 2)
        try:
            models.File.objects.get(id=file1["id"])
            self.fail("File 1 was created")
        except models.File.DoesNotExist:
            pass

        try:
            models.File.objects.get(id=file2["id"])
            self.fail("File 2 was created")
        except models.File.DoesNotExist:
            pass

    def test_update_file(self):

        file = models.File.objects.create(**self.file_db_metadata)
        new_preset = format_presets.VIDEO_HIGH_RES

        response = self.sync_changes(
            [generate_update_event(file.id, FILE, {"preset": new_preset}, channel_id=self.channel.id)],
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            models.File.objects.get(id=file.id).preset_id, new_preset,
        )

    def test_update_file_no_channel(self):
        file_metadata = self.file_db_metadata
        contentnode_id = file_metadata.pop("contentnode_id")
        file = models.File.objects.create(**file_metadata)

        response = self.sync_changes(
            [generate_update_event(file.id, FILE, {"contentnode": contentnode_id}, channel_id=self.channel.id)],
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            models.File.objects.get(id=file.id).contentnode_id, contentnode_id,
        )

    def test_update_file_no_channel_permission(self):
        file = models.File.objects.create(**self.file_db_metadata)
        new_preset = format_presets.VIDEO_HIGH_RES

        self.channel.editors.remove(self.user)

        response = self.sync_changes(
            [generate_update_event(file.id, FILE, {"preset": new_preset}, channel_id=self.channel.id)],
        )
        self.assertEqual(len(response.data["disallowed"]), 1)
        self.assertNotEqual(
            models.File.objects.get(id=file.id).preset_id, new_preset,
        )

    def test_update_file_no_channel_edit_permission(self):
        file = models.File.objects.create(**self.file_db_metadata)
        new_preset = format_presets.VIDEO_HIGH_RES

        self.channel.editors.remove(self.user)
        self.channel.viewers.add(self.user)

        response = self.sync_changes(
            [generate_update_event(file.id, FILE, {"preset": new_preset}, channel_id=self.channel.id)],
        )
        self.assertEqual(len(response.data["disallowed"]), 1)
        self.assertNotEqual(
            models.File.objects.get(id=file.id).preset_id, new_preset,
        )

    def test_update_files(self):

        file1 = models.File.objects.create(**self.file_db_metadata)
        file2 = models.File.objects.create(**self.file_db_metadata)
        new_preset = format_presets.VIDEO_HIGH_RES

        response = self.sync_changes(
            [
                generate_update_event(file1.id, FILE, {"preset": new_preset}, channel_id=self.channel.id),
                generate_update_event(file2.id, FILE, {"preset": new_preset}, channel_id=self.channel.id),
            ],
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            models.File.objects.get(id=file1.id).preset_id, new_preset,
        )
        self.assertEqual(
            models.File.objects.get(id=file2.id).preset_id, new_preset,
        )

    def test_update_file_empty(self):

        file = models.File.objects.create(**self.file_db_metadata)
        response = self.sync_changes([generate_update_event(file.id, FILE, {}, channel_id=self.channel.id)])
        self.assertEqual(response.status_code, 200, response.content)

    def test_update_file_unwriteable_fields(self):

        file = models.File.objects.create(**self.file_db_metadata)
        response = self.sync_changes(
            [generate_update_event(file.id, FILE, {"not_a_field": "not_a_value"}, channel_id=self.channel.id)],
        )
        self.assertEqual(response.status_code, 200, response.content)

    def test_delete_file(self):

        file = models.File.objects.create(**self.file_db_metadata)

        self.client.force_authenticate(user=self.user)
        response = self.sync_changes([generate_delete_event(file.id, FILE, channel_id=self.channel.id)])
        self.assertEqual(response.status_code, 200, response.content)
        try:
            models.File.objects.get(id=file.id)
            self.fail("File was not deleted")
        except models.File.DoesNotExist:
            pass

    def test_delete_files(self):
        file1 = models.File.objects.create(**self.file_db_metadata)

        file2 = models.File.objects.create(**self.file_db_metadata)

        self.client.force_authenticate(user=self.user)
        response = self.sync_changes(
            [
                generate_delete_event(file1.id, FILE, channel_id=self.channel.id),
                generate_delete_event(file2.id, FILE, channel_id=self.channel.id),
            ],
        )
        self.assertEqual(response.status_code, 200, response.content)
        try:
            models.File.objects.get(id=file1.id)
            self.fail("File 1 was not deleted")
        except models.File.DoesNotExist:
            pass

        try:
            models.File.objects.get(id=file2.id)
            self.fail("File 2 was not deleted")
        except models.File.DoesNotExist:
            pass


class CRUDTestCase(StudioAPITestCase):
    @property
    def file_metadata(self):
        return {
            "id": uuid.uuid4().hex,
            "contentnode": self.channel.main_tree.get_descendants().first().id,
            "checksum": uuid.uuid4().hex,
            "preset": format_presets.AUDIO,
            "file_format": file_formats.MP3,
            "uploaded_by": self.user.id,
        }

    @property
    def file_db_metadata(self):
        return {
            "id": uuid.uuid4().hex,
            "contentnode_id": self.channel.main_tree.get_descendants().first().id,
            "checksum": uuid.uuid4().hex,
            "preset_id": format_presets.AUDIO,
            "file_format_id": file_formats.MP3,
            "uploaded_by": self.user,
        }

    def setUp(self):
        super(CRUDTestCase, self).setUp()
        self.channel = testdata.channel()
        self.user = testdata.user()
        self.channel.editors.add(self.user)

    def test_cannot_create_file(self):
        self.client.force_authenticate(user=self.user)
        file = self.file_metadata
        response = self.client.post(reverse("file-list"), file, format="json",)
        self.assertEqual(response.status_code, 405, response.content)
        try:
            models.File.objects.get(id=file["id"])
            self.fail("File was created")
        except models.File.DoesNotExist:
            pass

    def test_update_file(self):
        file = models.File.objects.create(**self.file_db_metadata)
        new_preset = format_presets.VIDEO_HIGH_RES

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("file-detail", kwargs={"pk": file.id}),
            {"preset": new_preset},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            models.File.objects.get(id=file.id).preset_id, new_preset,
        )

    def test_update_file_no_channel(self):
        file_metadata = self.file_db_metadata
        contentnode_id = file_metadata.pop("contentnode_id")
        file = models.File.objects.create(**file_metadata)

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("file-detail", kwargs={"pk": file.id}),
            {"contentnode": contentnode_id},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            models.File.objects.get(id=file.id).contentnode_id, contentnode_id,
        )

    def test_update_file_no_channel_permission(self):
        file = models.File.objects.create(**self.file_db_metadata)
        new_preset = format_presets.VIDEO_HIGH_RES

        self.channel.editors.remove(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("file-detail", kwargs={"pk": file.id}),
            {"preset": new_preset},
            format="json",
        )
        self.assertEqual(response.status_code, 404, response.content)
        self.assertNotEqual(
            models.File.objects.get(id=file.id).preset_id, new_preset,
        )

    def test_update_file_no_channel_edit_permission(self):
        file = models.File.objects.create(**self.file_db_metadata)
        new_preset = format_presets.VIDEO_HIGH_RES

        self.channel.editors.remove(self.user)
        self.channel.viewers.add(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("file-detail", kwargs={"pk": file.id}),
            {"preset": new_preset},
            format="json",
        )
        self.assertEqual(response.status_code, 404, response.content)
        self.assertNotEqual(
            models.File.objects.get(id=file.id).preset_id, new_preset,
        )

    def test_update_file_no_node_permission(self):
        file = models.File.objects.create(**self.file_db_metadata)
        new_channel = testdata.channel()
        new_channel_node = new_channel.main_tree.get_descendants().first().id

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("file-detail", kwargs={"pk": file.id}),
            {"contentnode": new_channel_node},
            format="json",
        )
        self.assertEqual(response.status_code, 400, response.content)

    def test_update_file_no_assessmentitem_permission(self):
        file = models.File.objects.create(**self.file_db_metadata)
        new_channel = testdata.channel()
        new_channel_exercise = (
            new_channel.main_tree.get_descendants()
            .filter(kind_id=content_kinds.EXERCISE)
            .first()
        )
        new_channel_assessmentitem = new_channel_exercise.assessment_items.first().id

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("file-detail", kwargs={"pk": file.id}),
            {"assessment_item": new_channel_assessmentitem},
            format="json",
        )
        self.assertEqual(response.status_code, 400, response.content)

    def test_update_file_empty(self):

        file = models.File.objects.create(**self.file_db_metadata)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("file-detail", kwargs={"pk": file.id}), {}, format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)

    def test_update_file_unwriteable_fields(self):

        file = models.File.objects.create(**self.file_db_metadata)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("file-detail", kwargs={"pk": file.id}),
            {"not_a_field": "not_a_value"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)

    def test_delete_file(self):
        file = models.File.objects.create(**self.file_db_metadata)

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse("file-detail", kwargs={"pk": file.id}))
        self.assertEqual(response.status_code, 204, response.content)
        try:
            models.File.objects.get(id=file.id)
            self.fail("File was not deleted")
        except models.File.DoesNotExist:
            pass


class UploadFileURLTestCase(StudioAPITestCase):
    def setUp(self):
        super(UploadFileURLTestCase, self).setUp()
        self.user = testdata.user()
        self.file = {
            "size": 1000,
            "checksum": uuid.uuid4().hex,
            "name": "le_studio",
            "file_format": file_formats.MP3,
            "preset": format_presets.AUDIO,
            "duration": 10.123
        }

    def test_required_keys(self):
        del self.file["name"]

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("file-upload-url"), self.file, format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_duration_invalid(self):
        self.file["duration"] = '1.23'

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("file-upload-url"), self.file, format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_insufficient_storage(self):
        self.file["size"] = 100000000000000

        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("file-upload-url"), self.file, format="json",)

        self.assertEqual(response.status_code, 412)

    def test_upload_url(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("file-upload-url"), self.file, format="json",)
        self.assertEqual(response.status_code, 200)
        file = models.File.objects.get(checksum=self.file["checksum"])
        self.assertEqual(11, file.duration)
