from imagekit.processors import ResizeToFill, ResizeToFit

from pilkit.processors.resize import ResizeCanvas


class PositionCrop(object):
    """
    Processor to create custom image crops

    """

    def __init__(self, options):
        self.crop_position_field = options['crop_field']
        self.resize_method = options['resize_method']
        self.width = options['width']
        self.height = options['height']
        self.upscale = options['upscale'] or False
        
    def process(self, image, instance):
        print 'process position crop instance'


        #Step 1, crop based on crop position
        crop_value = getattr(instance, self.crop_position_field)
        print 'crop_value %s'%(crop_value)
        if crop_value and crop_value != '':
            crop_x = int(0-crop_value.x)
            crop_y = int(0-crop_value.y)
            crop_w = int(crop_value.width)
            crop_h = int(crop_value.height)


            print 'crop value %s %s %s %s'%(crop_x, crop_y, crop_w, crop_h)

            cropper = ResizeCanvas(crop_w, crop_h, None, None, crop_x, crop_y)
            cropped = cropper.process(image)
        else:
            #skip cropping if crop values not specified
            cropped = image

        #Step 2, resize to correct width and height:
        if self.resize_method == 'fit':
            resizer = ResizeToFit(self.width, self.height, None, self.upscale)            
        else:
            resizer = ResizeToFill(self.width, self.height, None, self.upscale)
        
        resized = resizer.process(cropped)
        return resized

