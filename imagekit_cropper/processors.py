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
        original_width = image.size[0]
        original_height = image.size[1]
        
        # print 'process %s :: original width %s original height %s || SETTINGS %s - %s - %s upscale? %s crop? %s, %s, %s, %s'%(instance, original_width, original_height, self.width, self.height, self.resize_method, self.upscale, crop_value.x, crop_value.y, crop_value.width, crop_value.height)
        is_empty_cropper = crop_value == None or crop_value == '' or (crop_value.width==None and crop_value.height==None)
        if is_empty_cropper:
            #Set crop with inital crop.

            crop_w = self.width#width if self.width is None else self.width
            crop_h = self.height#height if self.height is None else self.height

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
        crop_w = None if crop_value.width is None else int(crop_value.width)
        crop_h = None if crop_value.height is None else int(crop_value.height)

        # print "Resize canvas: %s, %s, %s, %s"%(crop_x, crop_y, crop_w, crop_h)
        cropper = ResizeCanvas(crop_w, crop_h, None, None, crop_x, crop_y)
        cropped = cropper.process(image)
       

        

        #Step 2, resize to correct width and height:
        if self.resize_method == 'fit':
            width = None if not self.width else self.width
            height = None if not self.height else self.height
            if height==None:
                # print 'height = (%s/%s) * %s'%(width, original_width, original_height)
                height = int(float(float(width)/float(original_width)) * float(original_height))
            elif width==None:
                width = int(float(float(height)/float(original_height)) * float(original_width))


            # print "Resize to fit: %s, %s"%(width, height)
            resizer = ResizeToFit(width, height, None, self.upscale)            
        else:
            width = cropped.size[0] if not self.width else self.width
            height = cropped.size[1] if not self.height else self.height
            # print "Resize to fill: %s, %s"%(crop_w, crop_h)
            resizer = ResizeToFill(width, height, None, self.upscale)
        
        # print 'Resize to %s - %s (%s - %s)'%(width, height, resizer.width, resizer.height)
        resized = resizer.process(cropped)
        return resized

