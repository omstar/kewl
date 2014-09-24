# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'GCMApiKey', fields ['user', 'app_name']
        db.delete_unique(u'embitel_framework_gcmapikey', ['user_id', 'app_name'])

        # Deleting model 'GCMApiKey'
        db.delete_table(u'embitel_framework_gcmapikey')

        # Adding model 'DeviceDetails'
        db.create_table(u'embitel_framework_devicedetails', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unique_key', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('unique_key_alias', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('device_type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('app_key', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('master_key', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('pn_status', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('auth_verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('channels', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'embitel_framework', ['DeviceDetails'])

        # Adding model 'ApplicationKey'
        db.create_table(u'embitel_framework_applicationkey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('app_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('api_key', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('emb_token', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('spare_1', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('spare_2', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal(u'embitel_framework', ['ApplicationKey'])

        # Adding unique constraint on 'ApplicationKey', fields ['user', 'app_name']
        db.create_unique(u'embitel_framework_applicationkey', ['user_id', 'app_name'])

        # Deleting field 'APNSDevices.phone_number'
        db.delete_column(u'embitel_framework_apnsdevices', 'phone_number')

        # Deleting field 'APNSDevices.unique_key'
        db.delete_column(u'embitel_framework_apnsdevices', 'unique_key')

        # Deleting field 'APNSDevices.unique_key_alias'
        db.delete_column(u'embitel_framework_apnsdevices', 'unique_key_alias')

        # Deleting field 'APNSDevices.pn_status'
        db.delete_column(u'embitel_framework_apnsdevices', 'pn_status')

        # Deleting field 'APNSDevices.app_key'
        db.delete_column(u'embitel_framework_apnsdevices', 'app_key')

        # Deleting field 'APNSDevices.channels'
        db.delete_column(u'embitel_framework_apnsdevices', 'channels')

        # Deleting field 'APNSDevices.device_type'
        db.delete_column(u'embitel_framework_apnsdevices', 'device_type')

        # Deleting field 'APNSDevices.auth_verified'
        db.delete_column(u'embitel_framework_apnsdevices', 'auth_verified')

        # Deleting field 'APNSDevices.master_key'
        db.delete_column(u'embitel_framework_apnsdevices', 'master_key')

        # Adding field 'APNSDevices.device_details'
        db.add_column(u'embitel_framework_apnsdevices', 'device_details',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['embitel_framework.DeviceDetails'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'GCMDevices.phone_number'
        db.delete_column(u'embitel_framework_gcmdevices', 'phone_number')

        # Deleting field 'GCMDevices.unique_key'
        db.delete_column(u'embitel_framework_gcmdevices', 'unique_key')

        # Deleting field 'GCMDevices.unique_key_alias'
        db.delete_column(u'embitel_framework_gcmdevices', 'unique_key_alias')

        # Deleting field 'GCMDevices.pn_status'
        db.delete_column(u'embitel_framework_gcmdevices', 'pn_status')

        # Deleting field 'GCMDevices.app_key'
        db.delete_column(u'embitel_framework_gcmdevices', 'app_key')

        # Deleting field 'GCMDevices.channels'
        db.delete_column(u'embitel_framework_gcmdevices', 'channels')

        # Deleting field 'GCMDevices.device_type'
        db.delete_column(u'embitel_framework_gcmdevices', 'device_type')

        # Deleting field 'GCMDevices.auth_verified'
        db.delete_column(u'embitel_framework_gcmdevices', 'auth_verified')

        # Deleting field 'GCMDevices.master_key'
        db.delete_column(u'embitel_framework_gcmdevices', 'master_key')

        # Deleting field 'GCMDevices.api_key'
        db.delete_column(u'embitel_framework_gcmdevices', 'api_key_id')

        # Deleting field 'GCMDevices.gcm_device_id'
        db.delete_column(u'embitel_framework_gcmdevices', 'gcm_device_id')

        # Adding field 'GCMDevices.application_key'
        db.add_column(u'embitel_framework_gcmdevices', 'application_key',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['embitel_framework.ApplicationKey'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'GCMDevices.device_details'
        db.add_column(u'embitel_framework_gcmdevices', 'device_details',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['embitel_framework.DeviceDetails'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Removing unique constraint on 'ApplicationKey', fields ['user', 'app_name']
        db.delete_unique(u'embitel_framework_applicationkey', ['user_id', 'app_name'])

        # Adding model 'GCMApiKey'
        db.create_table(u'embitel_framework_gcmapikey', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('spare_2', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('spare_1', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('app_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('api_key', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('emb_token', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'embitel_framework', ['GCMApiKey'])

        # Adding unique constraint on 'GCMApiKey', fields ['user', 'app_name']
        db.create_unique(u'embitel_framework_gcmapikey', ['user_id', 'app_name'])

        # Deleting model 'DeviceDetails'
        db.delete_table(u'embitel_framework_devicedetails')

        # Deleting model 'ApplicationKey'
        db.delete_table(u'embitel_framework_applicationkey')

        # Adding field 'APNSDevices.phone_number'
        db.add_column(u'embitel_framework_apnsdevices', 'phone_number',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'APNSDevices.unique_key'
        db.add_column(u'embitel_framework_apnsdevices', 'unique_key',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'APNSDevices.unique_key_alias'
        db.add_column(u'embitel_framework_apnsdevices', 'unique_key_alias',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'APNSDevices.pn_status'
        db.add_column(u'embitel_framework_apnsdevices', 'pn_status',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'APNSDevices.app_key'
        db.add_column(u'embitel_framework_apnsdevices', 'app_key',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'APNSDevices.channels'
        db.add_column(u'embitel_framework_apnsdevices', 'channels',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'APNSDevices.device_type'
        db.add_column(u'embitel_framework_apnsdevices', 'device_type',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'APNSDevices.auth_verified'
        db.add_column(u'embitel_framework_apnsdevices', 'auth_verified',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'APNSDevices.master_key'
        db.add_column(u'embitel_framework_apnsdevices', 'master_key',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'APNSDevices.device_details'
        db.delete_column(u'embitel_framework_apnsdevices', 'device_details_id')

        # Adding field 'GCMDevices.phone_number'
        db.add_column(u'embitel_framework_gcmdevices', 'phone_number',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'GCMDevices.unique_key'
        db.add_column(u'embitel_framework_gcmdevices', 'unique_key',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'GCMDevices.unique_key_alias'
        db.add_column(u'embitel_framework_gcmdevices', 'unique_key_alias',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'GCMDevices.pn_status'
        db.add_column(u'embitel_framework_gcmdevices', 'pn_status',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'GCMDevices.app_key'
        db.add_column(u'embitel_framework_gcmdevices', 'app_key',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'GCMDevices.channels'
        db.add_column(u'embitel_framework_gcmdevices', 'channels',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'GCMDevices.device_type'
        db.add_column(u'embitel_framework_gcmdevices', 'device_type',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'GCMDevices.auth_verified'
        db.add_column(u'embitel_framework_gcmdevices', 'auth_verified',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'GCMDevices.master_key'
        db.add_column(u'embitel_framework_gcmdevices', 'master_key',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'GCMDevices.api_key'
        db.add_column(u'embitel_framework_gcmdevices', 'api_key',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['embitel_framework.GCMApiKey'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'GCMDevices.gcm_device_id'
        db.add_column(u'embitel_framework_gcmdevices', 'gcm_device_id',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'GCMDevices.application_key'
        db.delete_column(u'embitel_framework_gcmdevices', 'application_key_id')

        # Deleting field 'GCMDevices.device_details'
        db.delete_column(u'embitel_framework_gcmdevices', 'device_details_id')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'embitel_framework.apnsdevices': {
            'Meta': {'object_name': 'APNSDevices', '_ormbases': [u'push_notifications.APNSDevice']},
            u'apnsdevice_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['push_notifications.APNSDevice']", 'unique': 'True', 'primary_key': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'device_details': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['embitel_framework.DeviceDetails']", 'null': 'True', 'blank': 'True'}),
            'p12_certificate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['embitel_framework.P12Certificate']", 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'embitel_framework.applicationkey': {
            'Meta': {'unique_together': "(('user', 'app_name'),)", 'object_name': 'ApplicationKey'},
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'app_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'emb_token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'spare_1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'spare_2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'embitel_framework.devicedetails': {
            'Meta': {'object_name': 'DeviceDetails'},
            'app_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'auth_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'channels': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'device_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'pn_status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'unique_key': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'unique_key_alias': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'embitel_framework.gcmdevices': {
            'Meta': {'object_name': 'GCMDevices', '_ormbases': [u'push_notifications.GCMDevice']},
            'application_key': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['embitel_framework.ApplicationKey']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'device_details': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['embitel_framework.DeviceDetails']", 'null': 'True', 'blank': 'True'}),
            u'gcmdevice_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['push_notifications.GCMDevice']", 'unique': 'True', 'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'embitel_framework.p12certificate': {
            'Meta': {'unique_together': "(('user', 'app_name'),)", 'object_name': 'P12Certificate'},
            'app_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'emb_token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'p12_password': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'pem_file': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'spare_1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'spare_2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'push_notifications.apnsdevice': {
            'Meta': {'object_name': 'APNSDevice'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'device_id': ('uuidfield.fields.UUIDField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'registration_id': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'push_notifications.gcmdevice': {
            'Meta': {'object_name': 'GCMDevice'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'device_id': ('push_notifications.fields.HexIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'registration_id': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['embitel_framework']