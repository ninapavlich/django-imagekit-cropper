# from imagekit import hashers
# from imagekit import ImageSpec, register
# from imagekit.models import ProcessedImageField

# from imagekit.registry import generator_registry, cachefile_registry
# from imagekit.specs.sourcegroups import ImageFieldSourceGroup, ModelSignalRouter, ik_model_receiver
from imagekit.utils import  call_strategy_method
# from imagekit.cachefiles import ImageCacheFile
# from imagekit.exceptions import MissingSource
from imagekit.signals import source_saved
from imagekit.registry import cachefile_registry, generator_registry

spec_data_field_hash = {}

class InstanceSourceGroupRegistry(object):
    """
    EXTENDS InstanceSourceGroupRegistry

    """
    _signals = {
        source_saved: 'on_source_saved',
    }

    def __init__(self):
        self._source_groups = {}
        for signal in self._signals.keys():
            signal.connect(self.source_group_receiver)

    def register(self, generator_id, source_group, data):
        
        from imagekit.specs.sourcegroups import SourceGroupFilesGenerator
        generator_ids = self._source_groups.setdefault(source_group, set())
        generator_ids.add(generator_id)
        spec_data_field_hash[generator_id] = data
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

        # Ignore signals from unregistered groups.
        if source_group not in self._source_groups:
            return


        #OVERRIDE HERE -- pass specs into generator object
        specs = [generator_registry.get(id, source=source, specs=spec_data_field_hash[id]) for id in
                self._source_groups[source_group]]
        callback_name = self._signals[signal]
        #END OVERRIDE

        for spec in specs:
            file = ImageCacheFile(spec)
            call_strategy_method(file, callback_name)

instance_source_group_registry = InstanceSourceGroupRegistry()