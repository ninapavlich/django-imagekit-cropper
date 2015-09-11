from django.contrib.admin import widgets
from django.contrib.admin.utils import help_text_for_field
from django.utils.safestring import mark_safe

class ImageCropWidget(widgets.AdminTextInputWidget):
	image_model = None

	class Media:
		css = {
			'all': ('imagekit_cropper/jcrop/css/jquery.Jcrop.css', 'imagekit_cropper/css/imagecrop.css',)
		}
		js = ('imagekit_cropper/js/vendor/jquery.js','imagekit_cropper/js/imagecrop.js','imagekit_cropper/jcrop/js/jquery.Jcrop.js')
	
	def __init__(self, properties, help_text='', *args, **kwargs):
		self.properties = properties
		self.help_text = help_text
		
		return super(ImageCropWidget, self).__init__(*args, **kwargs)

		

	def get_crop_containers(self):
		properties = self.properties
		if 'aspect_ratio' in self.properties:
			return '<div class="image-cropper" data-width="%s" data-height="%s" data-ratio="%s" \
			data-resize-method="%s" data-source="%s" data-upscale="%s" ></div>\
			'%(self.properties['min_width'], self.properties['min_height'],
			self.properties['aspect_ratio'], self.properties['resize_method'],
			self.properties['source'], self.properties['upscale'])

		else:
			return '<div class="image-cropper" data-width="%s" data-height="%s" \
				data-resize-method="%s" data-source="%s" data-upscale="%s" ></div>\
				'%(self.properties['width'], 
				self.properties['height'], self.properties['resize_method'],
				self.properties['source'], self.properties['upscale'])

	def render(self, name, value, attrs=None):
		rendered = super(ImageCropWidget, self).render(name, value, attrs)
		return mark_safe('<div class="image-crop-container">%s%s<div \
			class="image-crop-data"><p class="grp-help">%s</p></div>\
			</div>'%(rendered, self.get_crop_containers(), self.help_text))