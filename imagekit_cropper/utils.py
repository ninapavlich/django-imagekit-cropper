import inspect

from django.conf import settings
from django.db import models
from django.db.models.signals import post_init, post_save
from django.dispatch import Signal
from django.utils.functional import wraps



from imagekit import hashers
from imagekit import ImageSpec, register
from imagekit.models import ProcessedImageField
from imagekit.models.fields.utils import ImageSpecFileDescriptor
from imagekit.registry import generator_registry, cachefile_registry
from imagekit.specs.sourcegroups import ImageFieldSourceGroup, ModelSignalRouter, ik_model_receiver
from imagekit.utils import  call_strategy_method
from imagekit.cachefiles import ImageCacheFile
from imagekit.exceptions import MissingSource



from pilkit.processors import ProcessorPipeline
from pilkit.utils import open_image, img_to_fobj


hack_spec_field_hash = {}
hack_source_field_hash = {}
instance_source_saved = Signal()


def instance_ik_model_receiver(fn):
    """
    A method decorator that filters out sign_original_specals coming from models that don't
    have fields that function as ImageFieldSourceGroup sources.

    """
    @wraps(fn)
    def receiver(self, sender, **kwargs):
        # print 'inspect.isclass(sender? %s'%(inspect.isclass(sender))
        if not inspect.isclass(sender):
            return
        for src in self._source_groups:
            if issubclass(sender, src.model_class):
                fn(self, sender=sender, **kwargs)

                # If we find a match, return. We don't want to handle the signal
                # more than once.
                return
    return receiver

class InstanceSourceGroupRegistry(object):
    """
    The source group registry is responsible for listening to source_* signals
    on source groups, and relaying them to the image generated file strategies
    of the appropriate generators.

    In addition, registering a new source group also registers its generated
    files with that registry.

    """
    _signals = {
        instance_source_saved: 'on_source_saved',
    }

    def __init__(self):
        self._source_groups = {}
        for signal in self._signals.keys():
            signal.connect(self.source_group_receiver)

    def register(self, generator_id, source_group):
        from imagekit.specs.sourcegroups import SourceGroupFilesGenerator
        hack_source_field_hash[source_group] = generator_id
        generator_ids = self._source_groups.setdefault(source_group, set())
        generator_ids.add(generator_id)
        cachefile_registry.register(generator_id,
                SourceGroupFilesGenerator(source_group, generator_id))

    def unregister(self, generator_id, source_group):
        from imagekit.specs.sourcegroups import SourceGroupFilesGenerator
        generator_ids = self._source_groups.setdefault(source_group, set())
        if generator_id in generator_ids:
            generator_ids.remove(generator_id)
            cachefile_registry.unregister(generator_id,
                    SourceGroupFilesGenerator(source_group, generator_id))

    def source_group_receiver(self, sender, source, signal, **kwargs):
        """
        Relay source group signals to the appropriate spec strategy.

        """
        from imagekit.cachefiles import ImageCacheFile
        source_group = sender

        instance = kwargs['instance']

        # Ignore signals from unregistered groups.
        if source_group not in self._source_groups:
            return

        #HOOK -- update source to point to image file.
        for id in self._source_groups[source_group]:

            spec_to_update = generator_registry.get(id, source=source, instance=instance, field=hack_spec_field_hash[id])            
                        
        specs = [generator_registry.get(id, source=source, instance=instance, field=hack_spec_field_hash[id]) for id in
                self._source_groups[source_group]]
        callback_name = self._signals[signal]
        # print 'callback_name? %s'%(callback_name)

        for spec in specs:
            file = ImageCacheFile(spec)
            # print 'SEPC %s file %s'%(spec, file)
            call_strategy_method(file, callback_name)

instance_source_group_registry = InstanceSourceGroupRegistry()

class InstanceModelSignalRouter(object):

    def __init__(self):
        self._source_groups = []

        #NEW HOOK -- tweak uid
        uid = 'instance_ik_spec_field_receivers'
        post_init.connect(self.post_init_receiver, dispatch_uid=uid)
        post_save.connect(self.post_save_receiver, dispatch_uid=uid)

    def add(self, source_group):
        self._source_groups.append(source_group)

    def init_instance(self, instance):
        instance._ik = getattr(instance, '_ik', {})

    def update_source_hashes(self, instance):
        """
        Stores hashes of the source image files so that they can be compared
        later to see whether the source image has changed (and therefore whether
        the spec file needs to be regenerated).

        """
        self.init_instance(instance)
        instance._ik['source_hashes'] = dict(
            (attname, hash(getattr(instance, attname)))
            for attname in self.get_source_fields(instance))
        return instance._ik['source_hashes']

    def get_source_fields(self, instance):
        """
        Returns a list of the source fields for the given instance.
        """
        return set(src.image_field
                   for src in self._source_groups
                   if isinstance(instance, src.model_class))

    @instance_ik_model_receiver
    def post_save_receiver(self, sender, instance=None, created=False, raw=False, **kwargs):
        if not raw:
            self.init_instance(instance)
            old_hashes = instance._ik.get('source_hashes', {}).copy()
            new_hashes = self.update_source_hashes(instance)
            source_fields = self.get_source_fields(instance)            
            for attname in source_fields:
                file = getattr(instance, attname)
                if file:
                    #TODO -- check here
                    #and old_hashes.get(attname) != new_hashes[attname]:
                    self.dispatch_signal(instance_source_saved, file, sender, instance,
                                         attname)

    @instance_ik_model_receiver
    def post_init_receiver(self, sender, instance=None, **kwargs):
        self.init_instance(instance)
        source_fields = self.get_source_fields(instance)
        local_fields = dict((field.name, field)
                            for field in instance._meta.local_fields
                            if field.name in source_fields)
        instance._ik['source_hashes'] = dict(
            (attname, hash(file_field))
            for attname, file_field in local_fields.items())
    

    def dispatch_signal(self, signal, file, model_class, instance, attname):
        for source_group in self._source_groups:
            if issubclass(model_class, source_group.model_class) and source_group.image_field == attname:
                #NEW HOOK -- send instance
                hack_source_group_lookup = hack_source_field_hash[source_group]
                hack_field_lookup = hack_spec_field_hash[hack_source_group_lookup]
                signal.send(sender=source_group, source=file, instance=instance, field=hack_field_lookup)

instance_model_signal_router = InstanceModelSignalRouter()

class InstanceFieldSourceGroup(ImageFieldSourceGroup):
    def __init__(self, model_class, image_field):
        self.model_class = model_class
        self.image_field = image_field
        instance_model_signal_router.add(self)

class InstanceProcessorPipeline(ProcessorPipeline):
    def process(self, img, instance):
        for proc in self:
            img = proc.process(img, instance)
        return img


class InstanceSpecFileDescriptor(ImageSpecFileDescriptor):

    
    def __get__(self, instance, owner):
        # print 'get %s - %s. attname: %s field %s source_field_name: %s'%(instance, owner, self.attname, self.field, self.source_field_name)

        if instance is None:
            return self.field
        else:
            source = getattr(instance, self.source_field_name)
            spec = self.field.get_spec(source=source, instance=instance)
            
            file = ImageCacheFile(spec)

            instance.__dict__[self.attname] = file
            return file

    def __set__(self, instance, value):
        instance.__dict__[self.attname] = value

class InstanceSpec(ImageSpec):

    
    def __init__(self, source, instance, field):
        self.source = source
        self.instance = instance
        self.field = field
        # print 'FIELD %s'%(field.extra_hash_key_values)
        # self.extra_hash_key_values = None
                
        super(InstanceSpec, self).__init__(source)

    def generate(self):
        
        if not self.source:
            raise MissingSource("The spec '%s' has no source file associated"
                                " with it." % self)

        # TODO: Move into a generator base class
        # TODO: Factor out a generate_image function so you can create a generator and only override the PIL.Image creating part. (The tricky part is how to deal with original_format since generator base class won't have one.)
        try:
            img = open_image(self.source)
        except ValueError:

            # Re-open the file -- https://code.djangoproject.com/ticket/13750
            self.source.open()
            img = open_image(self.source)

        original_format = img.format       

        # Run the processors
        img = ProcessorPipeline(self.field.processors or []).process(img)

        #HOOK -- now process instance processors
        img = InstanceProcessorPipeline(self.field.instance_processors or []).process(img, self.instance)            

        format = self.field.format or img.format or original_format or 'JPEG'
        options = self.options or {}
        fobj = img_to_fobj(img, format, self.autoconvert, **options)
        # print 'fobj? %s - %s - %s'%(fobj, img, format)
        # print options
        return fobj

    def get_hash(self):
        
        keys = [
            self.source.name,
            self.field.processors,
            self.field.instance_processors,
            self.field.format,
            self.field.options,
            self.autoconvert,
        ]
        instance = self.instance
        
        #Use the actual values of the fields to hash the instance
        #REQUIRES INSTANCE:
        for extra_field in self.field.extra_hash_key_values:
            field = getattr(self.instance, extra_field)
            field_hash = "%s_%s"%(extra_field, field)
            # print 'field_hash %s'%(field_hash)
            keys.append(field_hash)

        # print 'pickle keys: %s'%(keys)
        return hashers.pickle(keys)




