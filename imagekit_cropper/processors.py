from imagekit.processors import ResizeToFill, ResizeToFit

from pilkit.processors.resize import ResizeCanvas


class PositionCrop(object):
    """
    Processor to create custom image crops

    """



    def __init__(self, options):
        self.options = options
        self.crop_position_field = options['crop_field']
        self.resize_method = options['resize_method']
        self.width = options['width']
        self.height = options['height']
        self.upscale = options['upscale'] or False

    def process(self, image, instance):
        
        #Step 1, crop based on crop position
        crop_value = getattr(instance, self.crop_position_field)
        width = image.size[0]
        height = image.size[1]
        
        # print 'process %s :: original width %s original height %s || SETTINGS %s - %s - %s upscale? %s crop? %s, %s, %s, %s'%(instance, width, height, self.width, self.height, self.resize_method, self.upscale, crop_value.x, crop_value.y, crop_value.width, crop_value.height)
        is_empty_cropper = crop_value == None or crop_value == '' or (crop_value.width==None and crop_value.height==None)
        if is_empty_cropper:
            #Set crop with inital crop.

            crop_w = width if self.width is None else self.width
            crop_h = height if self.height is None else self.height

            if self.resize_method == 'fit':
                # print "Resize to fit: %s, %s"%(crop_w, crop_h)
                resizer = ResizeToFit(crop_w, crop_h, None, self.upscale)            
            else:
                # print "Resize to fill: %s, %s"%(crop_w, crop_h)
                resizer = ResizeToFill(crop_w, crop_h, None, self.upscale)

            resized = resizer.process(image)
            return resized
            
            
        crop_x = 0 if crop_value.x is None else int(0-crop_value.x)
        crop_y = 0 if crop_value.y is None else int(0-crop_value.y)
        crop_w = width if crop_value.width is None else int(crop_value.width)
        crop_h = height if crop_value.height is None else int(crop_value.height)

        cropper = ResizeCanvas(crop_w, crop_h, None, None, crop_x, crop_y)
        cropped = cropper.process(image)
       

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

