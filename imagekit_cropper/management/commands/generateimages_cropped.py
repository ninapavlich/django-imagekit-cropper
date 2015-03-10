import re
import traceback

from django.core.management.base import BaseCommand

from imagekit.registry import generator_registry, cachefile_registry
from imagekit.exceptions import MissingSource
from imagekit.utils import  call_strategy_method
from imagekit.cachefiles import ImageCacheFile

from imagekit_cropper.utils import hack_spec_field_hash


class Command(BaseCommand):
    help = ("""Generate files for the specified image generators (or all of them if
none was provided). Simple, glob-like wildcards are allowed, with *
matching all characters within a segment, and ** matching across
segments. (Segments are separated with colons.) So, for example,
"a:*:c" will match "a:b:c", but not "a:b:x:c", whereas "a:**:c" will
match both. Subsegments are always matched, so "a" will match "a" as
well as "a:b" and "a:b:c".""")
    args = '[generator_ids]'

    def handle(self, *args, **options):
        generators = generator_registry.get_ids()

        if args:
            patterns = self.compile_patterns(args)
            generators = (id for id in generators if any(p.match(id) for p in patterns))

        for generator_id in generators:
            self.stdout.write('Validating generator: %s\n' % generator_id)


            try:
                for image_file in cachefile_registry.get(generator_id):
                    if image_file.name:
                        self.stdout.write('  %s\n' % image_file.name)
                        try:
                            image_file.generate()
                        except Exception as err:
                            self.stdout.write('\tFailed %s\n' % (err))
            except:
                print 'GENERATE: %s'%(generator_id)
                for k, v in cachefile_registry._cachefiles.items():
                    if generator_id in v:
                        #k is SourceGroupFilesGenerator
                       
                        model_class = k.source_group.model_class
                        image_field = k.source_group.image_field
                        all_objects = model_class.objects.all()

                        for instance in all_objects:
                            
                            try:
                                print '%s - %s'%(generator_id, instance)
                                source = getattr(instance, image_field)
                                field = hack_spec_field_hash[generator_id]
                                spec = generator_registry.get(generator_id, source=source, instance=instance, field=field)
                                file = ImageCacheFile(spec)
                                call_strategy_method(file, 'on_source_saved')                         

                            except Exception, err:
                                print traceback.format_exc()
                        

    def compile_patterns(self, generator_ids):
        return [self.compile_pattern(id) for id in generator_ids]

    def compile_pattern(self, generator_id):
        parts = re.split(r'(\*{1,2})', generator_id)
        pattern = ''
        for part in parts:
            if part == '*':
                pattern += '[^:]*'
            elif part == '**':
                pattern += '.*'
            else:
                pattern += re.escape(part)
        return re.compile('^%s(:.*)?$' % pattern)
