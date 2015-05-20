import inspect

from django.conf import settings
from django.db import models
from django.db.models.signals import post_init, post_save
from django.dispatch import Signal
from django.utils.functional import wraps

from imagekit import hashers
from imagekit import ImageSpec, register
from imagekit.utils import  get_field_info, open_image, process_image
from imagekit.cachefiles import ImageCacheFile
from imagekit.exceptions import MissingSource




class InstanceSpec(ImageSpec):

	
	def __init__(self, source, specs):

		instance, attname = get_field_info(source)
		self.specs = specs
		
		#Apply specs to instance
		for attr_name in specs:
			setattr(self, attr_name, specs[attr_name])

		self.source = source
		self.instance = instance
		self.attname = attname
		
		self.init_processors()
			
		super(InstanceSpec, self).__init__(source)

	def get_format(self):
		return self.format

	def init_processors(self):
		#Pass instance reference to image processors
		for instance_processor in self.processors:
			instance_processor.image_instance = self.instance

	def get_hash(self):
		keys = [
			self.source.name,
			self.get_format(),
			self.options,
			self.autoconvert
		]


		#Use custom hashing function
		for processor in self.processors:
			if hasattr(processor, 'get_hash'):
				keys.append(processor.get_hash())
			else:
				keys.append(processor)
		
		# print 'keys: %s'%(keys)
		pickled = hashers.pickle(keys)
		return pickled



class InstanceFormatSpec(InstanceSpec):

	
	def __init__(self, source, specs):
		super(InstanceFormatSpec, self).__init__(source, specs)

		self.update_format()
		

	#HACK TO UPDATE FORMAT BASED ON MODEL VALUE
	def get_format(self):
		if hasattr(self, 'instance') and hasattr(self, 'format_field'):
			return getattr(self.instance, self.format_field)
		return self.format

	def update_format(self):
		self.format = self.get_format()

	def generate(self):
		self.update_format()
		return super(InstanceFormatSpec, self).generate()

	def get_hash(self):
		self.update_format()
		return super(InstanceFormatSpec, self).get_hash()

	

		
register.generator('imagekit_cropper:instance_spec', InstanceSpec)
register.generator('imagekit_cropper:instance_format_spec', InstanceFormatSpec)


