/*!
 * nina@ninalp.com
 */

$image_cropper_jquery = jQuery.noConflict();

;(function ( $, window, document, undefined ) {


    // Create the defaults once
    var pluginName = "imageCropWidget",
        defaults = {
            imagePreviewWidth: "280px",
            maxUpscale: 2,
            warningUpscale: 1.5
        };

    // The actual plugin constructor
    function ImageCropWidget( element, options ) {
        this.element = element;

        this.options = $.extend( {}, defaults, options) ;

        this._defaults = defaults;
        this._name = pluginName;

        if (typeof window['image_crops'] == "undefined") {
           window['image_crops'] = {};
        }


        this.init();
    }

    ImageCropWidget.prototype = {

        init: function() {
            // this.jcrop_api;
            this.input_container = $(this.element).find('input')[0];

            this.original_width = -1;
            this.original_height = -1;
            
            this.crop_container = $(this.element).find('.image-cropper')[0];
            this.data_container = $(this.element).find('.image-crop-data')[0];
            this.target_width = parseInt($(this.crop_container).data('width'));
            this.target_height = parseInt($(this.crop_container).data('height'));
            this.target_ratio = parseFloat($(this.crop_container).data('ratio'));
            this.target_resize_method = $(this.crop_container).data('resize-method');
            this.target_source = $(this.crop_container).data('source');
            this.target_upscale = $(this.crop_container).data('upscale').toLowerCase()=='true';
            //console.log("upscale? "+$(this.crop_container).data('upscale'))

            $(this.input_container).attr('data-original-value',$(this.input_container).attr('value'));

            this.help_text_container = $(this.data_container).find('.grp-help')[0];

            $(this.data_container).append( '<p class="upscale"></p>' );
            this.upscale_container = $(this.data_container).find('.upscale')[0];

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
            $(this.crop_container).html($('<img>'));
            var parent = this;
            this.image = $(this.crop_container).find('img')[0];

            
            if(this.image_source in window['image_crops']){

                var loaded = window['image_crops'][this.image_source]['loaded'];
                var image = window['image_crops'][this.image_source]['image'];
                if(loaded==true){
                    this.original_width = window['image_crops'][this.image_source]['original_width'];
                    this.original_height = window['image_crops'][this.image_source]['original_height'];
                    this.image_preview_source = window['image_crops'][this.image_source]['preview'];
                    this.render();
                }else{
                    image.load(function(event) {
                        parent.imageLoaded(event, this);
                    });    
                }
                
            }else{
                
                 
                this.original_width = -1;
                this.original_height = -1;
                var image = $("<img/>");
                if(this.image_source.substring(0,4).toLowerCase()==='http') {
                    $(image).attr("crossorigin", "anonymous");
                }
                window['image_crops'][this.image_source] = {'loaded':false,'image':image}

                image.load(function(event) {

                    window['image_crops'][parent.image_source]['loaded'] = true;
                    window['image_crops'][parent.image_source]['original_width'] = this.width;
                    window['image_crops'][parent.image_source]['original_height'] = this.height;
                    window['image_crops'][parent.image_source]['preview'] = parent.getResizedImage(this, $(parent.crop_container).width())

                    parent.imageLoaded(event, this);
                });

                var cachebuster = new Date().getTime();
                var cache_string = this.image_source.toLowerCase().indexOf('data:') >= 0? '' : "?v="+cachebuster;
                image.attr("src", this.image_source+cache_string);

            }

            

        },
        imageLoaded: function(event, image){
            
            this.original_width = image.width;
            this.original_height = image.height;
            this.image_preview_source = window['image_crops'][this.image_source]['preview'];

            this.render();
        },
        isCanvasSupported:function (){
          var elem = document.createElement('canvas');
          return !!(elem.getContext && elem.getContext('2d'));
        },
        getResizedImage:function(image, MAX_WIDTH, MAX_HEIGHT){

            if(this.isCanvasSupported()==false){
            //no canvas support :(
                return self.image_source;
            }

            var canvas = document.createElement('canvas');
            
            if(typeof(MAX_WIDTH) == 'undefined'){
                MAX_WIDTH = 800
            }
            if(typeof(MAX_HEIGHT) == 'undefined'){
                MAX_HEIGHT = 600
            }

            var width = image.width;
            var height = image.height;
             
            if (width > height) {
              if (width > MAX_WIDTH) {
                height *= MAX_WIDTH / width;
                width = MAX_WIDTH;
              }
            } else {
              if (height > MAX_HEIGHT) {
                width *= MAX_HEIGHT / height;
                height = MAX_HEIGHT;
              }
            }
            canvas.width = width;
            canvas.height = height;

            var ctx = canvas.getContext("2d");
            ctx.drawImage(image, 0, 0, width, height);

            var dataurl = canvas.toDataURL("image/png");
            return dataurl;
        },
        setImageSource: function(source) {            
            this.image_source = source;
            this.initialRender();
            //this.render();
        },
        setCropValue:function(preview_crop){
            crop = this.cropToRealValues(preview_crop);
            var pickled = crop.x+","+crop.y+","+crop.w+","+crop.h;
            $(this.input_container).val(pickled);
            $(this.input_container).attr('value',pickled);


            this.updateScaleNotification();
            
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

            if(isNaN(this.target_height) || isNaN(this.target_width)){
                var x = 0;
                var y = 0;
                var w = this.original_width;
                var h = this.original_height;

                //console.log("upscale? "+this.target_upscale+" target_w: "+this.target_width+" w: "+w+" target_height: "+this.target_height+" h? "+h)
            }else{
                var target_aspect_ratio = this.target_width / this.target_height;
                var current_aspect_ratio = this.original_width / this.original_height;

                if(target_aspect_ratio < current_aspect_ratio){
                    //then image height is our limiting factor
                    //and the crop width will be < the original width
                    var h = this.original_height;
                    var w = target_aspect_ratio * this.original_height;
                    var y = 0;
                    var x = 0.5*(this.original_width - w);

                }else{
                    //then image width is our limiting factor
                    //and the crop height will < the original height
                    var w = this.original_width;
                    var h = this.original_width / target_aspect_ratio;
                    var x = 0;
                    var y = 0.5*(this.original_height - h);               

                }

            }

            

            reset = {'x':x,'y':y,'w':w,'h':h}  
            // console.log("getResetCrop: "+reset)
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
            $(this.image).attr('src', this.image_preview_source);
            
            var aspect_ratio = isNaN(this.target_ratio)? this.target_width / this.target_height : this.target_ratio;
            
            var initial_crop = this.getCropValue();
            var minW = 1;
            var minH = 1;
            if(this.target_upscale==false){

                if(this.target_width > this.original_width){
                    minW = this.scaleToPreview(this.original_width);    
                }else{
                    minW = this.scaleToPreview(this.target_width);
                }

                if(this.target_height > this.original_height){
                    minH = this.scaleToPreview(this.original_height);    
                }else{
                    minH = this.scaleToPreview(this.target_height);
                }
            }
            
            
            
            $(this.image).Jcrop({
                onSelect: function(c){
                    parent.updateCoordinates(c)
                },
                onChange: function(c){
                    parent.updateCoordinates(c)
                },
                setSelect:   [ initial_crop.x, initial_crop.y, initial_crop.x+initial_crop.w, initial_crop.y+initial_crop.h ],
                aspectRatio: aspect_ratio,
                minSize: [minW, minH],
                allowSelect: false
            });
        },
        updateScaleNotification: function(){

            var scale_w = this.target_width / crop.w;
            var scale_h = this.target_height / crop.h;
            
            var warning_upscale = scale_w > 1.01 || scale_h > 1.01
            var warning_upscale_high = scale_w > this.options.warningUpscale || scale_h > this.options.warningUpscale;

            if(warning_upscale){
                var max = isNaN(scale_w)? scale_h : isNaN(scale_h)? scale_w : Math.max(scale_w, scale_h);
                $(this.upscale_container).text('This crop will up-scale the image by '+(this.formatUpscale(max))+"%. Increase your bounding box or upload a larger source image if possible.");                
            }

            if(this.target_upscale && warning_upscale){
                $(this.upscale_container).show();
            }else{
                $(this.upscale_container).hide();
            }
            
            if(this.target_upscale && warning_upscale_high){
                $(this.upscale_container).addClass('warning');                
            }else{
                $(this.upscale_container).removeClass('warning');                
            }
            

        },
        formatUpscale:function(number){
            return parseInt(100*(number-1));
        },
        addListeners: function() {
            //bind events
            var parent = this;
            $('#id_'+this.target_source).bind('change', function(event){
                var input = this;
                if (input.files && input.files[0]) {
                    var reader = new FileReader();
                    reader.onload = function (e) {   
                        $(parent.input_container).attr('value', '');
                        $(parent.input_container).val('');
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
            var current_value = $('.grp-cell.'+image_name+", .grp-row."+image_name).find(".file-upload a").attr('href')
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

})( $image_cropper_jquery, window, document );


$image_cropper_jquery( document ).ready(function() {
 $image_cropper_jquery(".image-crop-container").imageCropWidget();
});


