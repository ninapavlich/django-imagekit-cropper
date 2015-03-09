from django.db import models

from imagekit.models import ImageSpecField

from .utils import InstanceSpec, instance_source_group_registry, \
    InstanceSpecFileDescriptor, InstanceFieldSourceGroup



class InstanceSpecField(ImageSpecField):
    """
    Image spec field which passes the class instance to the processors

    """

    fields = None
    source = None

    def __init__(self, processors=None, instance_processors=None, format=None, options=None,
            source=None, cachefile_storage=None, autoconvert=None,
            cachefile_backend=None, cachefile_strategy=None, spec=None,
            id=None, hash_key_values=None):

        self.source = source
        
        spec = InstanceSpec
        spec.format = format
        spec.image_format = format
        spec.options = options
        spec.extra_hash_key_values = hash_key_values

        spec.processors = processors    
        spec.instance_processors = instance_processors        

        super(InstanceSpecField, self).__init__(None, None, None,
            source, cachefile_storage, autoconvert, cachefile_backend, 
            cachefile_strategy, spec, id)

    def contribute_to_class(self, cls, name):
        
        #HOOK for crop field
        def register_group(source):
            setattr(cls, name, InstanceSpecFileDescriptor(self, name, source))
            self._set_spec_id(cls, name)

            # Add the model and field as a source for this spec id
            instance_source_group_registry.register(self.spec_id, InstanceFieldSourceGroup(cls, source))            

        register_group(self.source)



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
    __metaclass__ = models.SubfieldBase
    
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
