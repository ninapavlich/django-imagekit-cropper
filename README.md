# django-imagekit-cropper
A library to enhance django-imagekit which allows you to specify your image variant crops:

![CKEditor Dialog](https://raw.github.com/ninapavlich/django-imagekit-cropper/master/docs/screenshots/crop_screenshot.png)

**InstanceSpecField** This is a class that extends ImageSpecField which passes the model instance to 
the processors so that you can access other model fields to process the image.

**InstanceFormatSpecField** This is a class that extends InstanceSpecField and can dynamically choose the image format (e.g. JPEG, PNG, GIF). PNGs have a much larger file size than JPEGs, but sometimes it's worth the filesize; this allows the admins to control on a per-image basis. Just pass a reference to the model field that returns a PIL-compatible file format.

**ImageCropField** This is a custom model field for setting the image crop. This uses a custom
widget to allow admins to visually crop the image.

**PositionCrop** This a custom processor which recieves the model instance and crops the image
using the image source and the value of the image crop field.

**FormatProcessor** This is a custom processor which implements resizing and outputs to a dynamic format.

**PositionAndFormatCrop** This processor extends PositionCrop and also implements dynamic format.

**WARNING:** This library is in very early alpha stages. I have only tested this on version django-imagekit==3.2.5

## Example Usage
```
    $ pip install django-imagekit-cropper
```

```
    #settings.py

    INSTALLED_APPS = (
        ...
        imagekit_cropper,
        ...
    )
```    


```python
    #models.py

    from imagekit_cropper.fields import ImageCropField, InstanceSpecField, InstanceFormatSpecField
    from imagekit_cropper.processors import PositionCrop, PositionAndFormatCrop, FormatProcessor

    image = models.ImageField(blank=True, null=True)
    
    #Example 1 - BASIC CROP FIELD
    width_1200_wide_crop_properties = {
        'source':'image',
        'crop_field':'width_1200_wide_crop', 
        'resize_method':'fill',
        'width':1200,
        'height':750, 
        'upscale':True
    }
    width_1200_wide_crop = ImageCropField(null=True, blank=True, 
        properties=width_1200_wide_crop_properties)

    width_1200_wide = InstanceSpecField( 
        source=width_1200_wide_crop_properties['source'], 
        options={'quality': 85}, 
        processors=[PositionCrop(width_1200_wide_crop_properties)])

    #Example 2 - DYNAMIC FORMAT FIELD
    
    
    width_1200_crop_properties = {
        'source':'image',
        'format_field':'get_format',
        'resize_method':'fit',
        'width':1200,
        'height':None, 
        'upscale':False
    }
    width_1200 = InstanceFormatSpecField( 
        source=width_1200_crop_properties['source'], 
        format_field=width_1200_crop_properties['format_field'],
        options={'quality': 95}, 
        processors=[FormatProcessor(width_1200_crop_properties)])
    
    use_png = models.BooleanField( default = False, 
        verbose_name='Use .PNG (instead of .JPG)')
        
    @property
    def get_format(self):
        if self.use_png:
            return 'PNG'
        return 'JPEG'


    #Example 3 - TWO SPECS USING THE SAME CROP

    square_crop_properties = {
        'source':'image',
        'crop_field':'square_crop', 
        'format_field':'get_format',
        'resize_method':'fill',
        'aspect_ratio':1,
        'min_width':400,
        'min_height':400,
        'upscale':False
    }
    square_crop = ImageCropField(null=True, blank=True, properties=square_crop_properties)

    square_200_crop_properties = copy.copy(square_crop_properties)
    square_200_crop_properties['width'] = 200
    square_200_crop_properties['height'] = 200
    
    square_200 = InstanceSpecField(
        format='PNG',
        source=square_200_crop_properties['source'], 
        options={'quality': 85}, 
        processors=[PositionCrop(square_200_crop_properties)]
    )

    square_400_crop_properties = copy.copy(square_crop_properties)
    square_400_crop_properties['width'] = 400
    square_400_crop_properties['height'] = 400

    square_400 = InstanceFormatSpecField(
        source=square_400_crop_properties['source'], 
        format_field=square_400_crop_properties['format_field'],
        options={'quality': 85}, 
        processors=[PositionAndFormatCrop(square_400_crop_properties)]
    )

```  

```python
    #admin.py

    from .forms import ImageAdminForm
    
    class ImageAdmin(models.ModelAdmin):
        form = ImageAdminForm

```        

```python
    #forms.py

    from django import forms
    from imagekit_cropper.widgets import ImageCropWidget    
    from .models import Image

    
    class ImageAdminForm(forms.ModelForm):
        square_150_crop = forms.CharField(widget=ImageCropWidget(properties=Image.square_150_crop_properties, help_text=Image.help['square_150_crop']))

        class Meta:
            model = Image

``` 

To generate images, you'll need to use this modified version of the generateimages command:
```
    $ python manage.py generateimages_cropped
```

