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
        
        #Step 1, crop based on crop position
        crop_value = getattr(instance, self.crop_position_field)
        if crop_value and crop_value != '':
            crop_x = int(0-crop_value.x)
            crop_y = int(0-crop_value.y)
            crop_w = int(crop_value.width)
            crop_h = int(crop_value.height)

            cropper = ResizeCanvas(crop_w, crop_h, None, None, crop_x, crop_y)
            cropped = cropper.process(image)
        else:
            #skip cropping if crop values not specified
            cropped = image

        width = cropped.size[0] if not self.width else self.width
        height = cropped.size[1] if not self.height else self.height

        #Step 2, resize to correct width and height:
        if self.resize_method == 'fit':
            resizer = ResizeToFit(width, height, None, self.upscale)            
        else:
            resizer = ResizeToFill(width, height, None, self.upscale)
        
        # print 'Resize to %s - %s (%s - %s)'%(width, height, resizer.width, resizer.height)
        resized = resizer.process(cropped)
        return resized

