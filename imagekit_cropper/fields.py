from django.db import models

from imagekit.models import ImageSpecField
from imagekit.models.fields.utils import ImageSpecFileDescriptor
from imagekit.registry import generator_registry, unregister
from imagekit.specs import SpecHost, create_spec_class
from imagekit.specs.sourcegroups import ImageFieldSourceGroup

from .specs import InstanceSpec, InstanceFormatSpec
from .registry import InstanceSourceGroupRegistry, instance_source_group_registry


class InstanceSpecField(ImageSpecField):
    """
    Image spec field which passes the class instance to the processors

    """


    fields = None
    source = None

    def __init__(self, processors=None, format=None, options=None,
            source=None, cachefile_storage=None, autoconvert=None,
            cachefile_backend=None, cachefile_strategy=None, spec=None,
            id=None):


        self.options = options
        self.format = format
        self.processors = processors

        
        #==== FROM ImageSpecField
        SpecHost.__init__(self, processors=processors, format=format,
                options=options, cachefile_storage=cachefile_storage,
                autoconvert=autoconvert,
                cachefile_backend=cachefile_backend,
                cachefile_strategy=cachefile_strategy, spec=spec,
                spec_id=id)

        # TODO: Allow callable for source. See https://github.com/matthewwithanm/django-imagekit/issues/158#issuecomment-10921664
        self.source = source
        #==== END FROM ImageSpecField

        self.spec = spec = self.get_spec_class() 


        data = self.get_spec_instance_attrs()
        for attr in data:
            setattr(self.spec, attr, data[attr])

        spec_id = id

        self._original_spec = spec

        #==== END FROM SpecHost

    def contribute_to_class(self, cls, name):
        
        descriptor = ImageSpecFileDescriptor(self, name, self.source)
        setattr(cls, name, descriptor)

        #Store spec instance info based on spec ID
        spec_id = ('%s:%s:%s' % (cls._meta.app_label,
                            cls._meta.object_name, name)).lower()
        
        #Un-register with default source group; use custom
        unregister.source_group(spec_id, ImageFieldSourceGroup(cls, self.source))
        instance_source_group_registry.register(spec_id, ImageFieldSourceGroup(cls, self.source), self.get_spec_instance_attrs())  

        # setattr(cls, name, InstanceSpecFileDescriptor(self, name, source))
        self._set_spec_id(cls, name)
        
    def get_spec(self, source):
        
        item = generator_registry.get(self.spec_id, source=source, specs=self.get_spec_instance_attrs())

        return item


    def get_spec_class(self):
        return InstanceSpec

    def get_spec_instance_attrs(self):
        return {'options': self.options, 'processors': self.processors, 'format': self.format} #override


class InstanceFormatSpecField(InstanceSpecField):

    def __init__(self, format_field, processors=None, format=None, options=None,
            source=None, cachefile_storage=None, autoconvert=None,
            cachefile_backend=None, cachefile_strategy=None, spec=None,
            id=None):
        
        self.format_field = format_field

        super(InstanceFormatSpecField, self).__init__(processors, format, 
            options, source, cachefile_storage, autoconvert, cachefile_backend, 
            cachefile_strategy, spec, id)

    def get_spec_instance_attrs(self):
        return {'options': self.options, 'processors': self.processors, 'format': self.format, 'format_field':self.format_field} #override

    def get_spec_class(self):
        return InstanceFormatSpec

class CropCoordinates(object):
    def __init__(self, x=None, y=None, width=None, height=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        if self.width or self.height:
            return "%s,%s,%s,%s"%(self.x, self.y, self.width, self.height)
        return ''

class ImageCropField(models.Field):
    """
    Model field for containing image crop dimensions

    """

    description = "Image crop coordinates"
    
    def __init__(self,properties, help_text=("A comma-separated list of crop coordinates"),verbose_name='imagecropfield', *args,**kwargs):
        self.name="ImageCropField",
        self.through = None
        self.help_text = help_text
        self.blank = True
        self.editable = True
        self.creates_table = False
        self.db_column = None
        self.serialize = False
        self.null = True
        self.creation_counter = models.Field.creation_counter        
        self.properties = properties
        # self.default_width = self.properties['width'] if self.properties['width'] else 1000
        # self.default_height = self.properties['height'] if self.properties['height'] else 1000
        models.Field.creation_counter += 1
        super(ImageCropField, self).__init__(*args, **kwargs)


    def deconstruct(self):
        name, path, args, kwargs = super(ImageCropField, self).deconstruct()
        kwargs['properties'] = self.properties
        return name, path, args, kwargs
        
        
    def db_type(self, connection):
        return 'varchar(100)'
    
    def to_python(self,value):
        
        if value in ( None,''):
            
            return CropCoordinates()
        else:
            if isinstance(value, CropCoordinates):
                return value
            else:

                if 'None' in value:
                    return CropCoordinates()

                split_items = value.split(',')

                

                x = float(split_items[0])
                y = float(split_items[1])
                w = float(split_items[2])
                h = float(split_items[3])

                args = [x,y,w,h]
                if len(args) != 4 and value is not None:
                    raise ValidationError("Invalid input for a CropCoordinates instance")
                return CropCoordinates(*args)
         

    def get_prep_value(self, value):
        if value:
            store_value = ','.join([str(value.x),str(value.y),str(value.width),str(value.height)])
            return store_value
        return None
    
    def get_internal_type(self):
        return 'CharField'
    
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)    
