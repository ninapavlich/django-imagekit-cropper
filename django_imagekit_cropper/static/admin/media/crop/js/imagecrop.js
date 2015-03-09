/*!
 * nina@ninalp.com
 */

 //TO DO: 
window['$'] = grp.jQuery;
window['jQuery'] = grp.jQuery;

;(function ( $, window, document, undefined ) {


    // Create the defaults once
    var pluginName = "imageCropWidget",
        defaults = {
            imagePreviewWidth: "300px"
        };

    // The actual plugin constructor
    function ImageCropWidget( element, options ) {
        this.element = element;

        this.options = $.extend( {}, defaults, options) ;

        this._defaults = defaults;
        this._name = pluginName;


        this.init();
    }

    ImageCropWidget.prototype = {

        init: function() {
            // this.jcrop_api;
            this.input_container = $(this.element).find('input')[0];

            this.original_width = -1;
            this.original_height = -1;
            
            this.crop_container = $(this.element).find('.image-cropper')[0];
            this.target_width = parseInt($(this.crop_container).data('width'));
            this.target_height = parseInt($(this.crop_container).data('height'));
            this.target_resize_method = $(this.crop_container).data('resize-method');
            this.target_source = $(this.crop_container).data('source');
            this.target_upscale = $(this.crop_container).data('upscale').toLowerCase()=='true';
            console.log("upscale? "+$(this.crop_container).data('upscale'))

            this.setImageSource(this.getSourceImage(this.target_source));
            
                
            this.addListeners();          

            this.render()
        },
        initialRender: function(){

            //destroy any previous instances
            //TODO
            // if(this.jcrop_api){
            //     console.log('destroy previous jcrop api.: '+this.jcrop_api+" "+typeof(this.jcrop_api))
            //     this.jcrop_api.destroy();
            //     this.jcrop_api = null;
            // }

            //create fresh instances...
            $(this.crop_container).html($('<img>'))
            this.image = $(this.crop_container).find('img')[0]; 

            this.original_width = -1;
            this.original_height = -1;
            var parent = this;
            $("<img/>").attr("src", this.image_source)
                .load(function() {
                    console.log("original width: "+this.width)

                    parent.original_width = this.width;
                    parent.original_height = this.height;
                    parent.render();
                });

        },
        setImageSource: function(source) {            
            this.image_source = source;
            this.initialRender();
            this.render();
        },
        setCropValue:function(preview_crop){
            crop = this.cropToRealValues(preview_crop);
            var pickled = crop.x+","+crop.y+","+crop.w+","+crop.h;
            $(this.input_container).val(pickled);
            $(this.input_container).attr('value',pickled);
        },
        getCropValue:function(){
            var pickled = $(this.input_container).attr('value');
            if(pickled=='' || typeof(pickled) == 'undefined'){
                //find a center crop.   
                var real = this.getResetCrop()

            }else{
                var split = pickled.split(',');
                var real = {'x':parseInt(split[0]),'y':parseInt(split[1]),'w':parseInt(split[2]),'h':parseInt(split[3])}
            }
            
            return this.cropToPreviewValues(real)
        },
        cropToPreviewValues:function(crop){
            return {'x':this.scaleToPreview(crop.x),'y':this.scaleToPreview(crop.y),'w':this.scaleToPreview(crop.w),'h':this.scaleToPreview(crop.h)}
        },
        cropToRealValues:function(crop){
            return {'x':this.scaleToReal(crop.x),'y':this.scaleToReal(crop.y),'w':this.scaleToReal(crop.w),'h':this.scaleToReal(crop.h)}
        },
        scaleToPreview:function(value){
            var scaler = $(this.image).width() / this.original_width;
            return Math.round(value*scaler);
        },
        scaleToReal:function(value){
            var scaler = this.original_width / $(this.image).width();
            return Math.round(value*scaler);
        },
        getResetCrop:function(){

            var target_aspect_ratio = this.target_width / this.target_height;
            var current_aspect_ratio = this.original_width / this.original_height;

            if(target_aspect_ratio < current_aspect_ratio){
                //then image height is our limiting factor
                //and the crop width will be < the original width
                var target_height = this.original_height;
                var target_width = target_aspect_ratio * this.original_height;
                var y = 0;
                var x = 0.5*(this.original_width - target_width);

            }else{
                //then image width is our limiting factor
                //and the crop height will < the original height
                var target_width = this.original_width;
                var target_height = this.original_width / target_aspect_ratio;
                var x = 0;
                var y = 0.5*(this.original_height - target_height);               

            }

            reset = {'x':x,'y':y,'w':target_width,'h':target_height}  
            console.log("getResetCrop: "+reset)
            return reset;
        },
        updateCoordinates: function(c){
            this.setCropValue(c);
        },
        render: function() {

            if(this.original_width < 0 || this.original_height < 0){
                //not ready. wait for original image to load
                return;
            }

            //Update view
            var parent = this;
            $(this.image).attr('width', this.options.imagePreviewWidth);
            $(this.image).attr('src', this.image_source);

            var aspect_ratio = this.target_width / this.target_height;
            var initial_crop = this.getCropValue();
            var minW = 0;
            var minH = 0;
            if(this.target_upscale==false){
                var minW = this.scaleToPreview(this.target_width);
                var minH = this.scaleToPreview(this.target_height);
            }
            
            // console.log("apply initial_crop: "+initial_crop.x+" minW: "+minW+" maxW: "+minW)
            
            $(this.image).Jcrop({
                onSelect: function(c){
                    parent.updateCoordinates(c)
                },
                onChange: function(c){
                    parent.updateCoordinates(c)
                },
                setSelect:   [ initial_crop.x, initial_crop.y, initial_crop.x+initial_crop.w, initial_crop.y+initial_crop.h ],
                aspectRatio: aspect_ratio,
                minSize: [minW, minH]
            });
        },

        addListeners: function() {
            //bind events
            var parent = this;
            $('#id_'+this.target_source).bind('change', function(event){
                var input = this;
                if (input.files && input.files[0]) {
                    var reader = new FileReader();
                    reader.onload = function (e) {   
                        parent.setImageSource(e.target.result);
                    }
                    reader.readAsDataURL(input.files[0]);
                }
            }); 

            $(this.input_container).bind('change', function(event){
                $(parent.input_container).attr('value', $(parent.input_container).val())
                parent.render();
            }) 
        },

        removeListeners: function() {
            //unbind events           
            $('#id_'+this.target_source).unbind('change');
            $(this.input_container).unbind('change');
        },
        getSourceImage:function(image_name){
            var current_value = $('.grp-cell.'+image_name).find(".file-upload a").attr('href')
            var input_value = $('#id_'+image_name).attr('value');

            if(typeof(input_value) == 'undefined'){
                if(typeof(current_value) == 'undefined'){
                    return '';
                }
                return current_value;
            }
            return input_value;

        }

    };

    // A really lightweight plugin wrapper around the constructor,
    // preventing against multiple instantiations
    $.fn[pluginName] = function ( options ) {
        return this.each(function () {
            if (!$.data(this, "plugin_" + pluginName)) {
                $.data(this, "plugin_" + pluginName,
                new ImageCropWidget( this, options ));
            }
        });
    };

})( jQuery, window, document );




$( document ).ready(function() {
 $(".image-crop-container").imageCropWidget();
});


