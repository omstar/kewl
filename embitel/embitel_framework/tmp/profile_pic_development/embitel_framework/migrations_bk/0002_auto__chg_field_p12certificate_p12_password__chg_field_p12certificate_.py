# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'P12Certificate.p12_password'
        db.alter_column(u'embitel_framework_p12certificate', 'p12_password', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'P12Certificate.emb_token'
        db.alter_column(u'embitel_framework_p12certificate', 'emb_token', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100))

        # Changing field 'P12Certificate.path'
        db.alter_column(u'embitel_framework_p12certificate', 'path', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200))

    def backwards(self, orm):

        # Changing field 'P12Certificate.p12_password'
        db.alter_column(u'embitel_framework_p12certificate', 'p12_password', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'P12Certificate.emb_token'
        db.alter_column(u'embitel_framework_p12certificate', 'emb_token', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True))

        # Changing field 'P12Certificate.path'
        db.alter_column(u'embitel_framework_p12certificate', 'path', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True))

    models = {
        u'embitel_framework.p12certificate': {
            'Meta': {'object_name': 'P12Certificate'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'emb_token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'p12_password': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'spare_1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'spare_2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['embitel_framework']