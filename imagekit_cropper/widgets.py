from django.forms import widgets

class ImageCropWidget(widgets.TextInput):
    image_model = None

    class Media:
        css = {
            'all': ('admin/media/crop/jcrop/css/jquery.Jcrop.css', 'admin/media/crop/css/imagecrop.css',)
        }
        js = ('admin/media/crop/js/imagecrop.js','admin/media/crop/jcrop/js/jquery.Jcrop.js')
    
    def __init__(self, properties, *args, **kwargs):
        self.properties = properties
        return super(ImageCropWidget, self).__init__(*args, **kwargs)

    def get_crop_containers(self):
        return '<div class="image-cropper" data-width="%s" data-height="%s" \
        data-resize-method="%s" data-source="%s" data-upscale="%s" ></div>\
            '%(self.properties['width'], 
            self.properties['height'], self.properties['resize_method'],
            self.properties['source'], self.properties['upscale'])

    def render(self, name, value, attrs=None):
        rendered = super(ImageCropWidget, self).render(name, value, attrs)
        return mark_safe('<div class="image-crop-container">%s%s</div>'%(rendered, self.get_crop_containers()))