$(document).ready(function(){
    $('#resultContainer').hide()
    $('#trainSection').hide()
    $('#submitBtn').attr('disabled', true)
    $('#errorMsg').hide()
    $('.loader').hide()
    $('#urlTextField').on('input', function() { 
        $('#submitBtn').attr('disabled', true)
        var urlPattern = /^(https?:\/\/)?(?:www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?((\w|-){11})(?:\S+)?$/;
//            /^(?:https?:\/\/)?(?:www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/watch\?((?=.*v=|embed\/|v\/|.+\?v=)((\w|-){11}))(?:\S+)?$/;
//            /(https?:\/\/)?(?:www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11}/;
        var youtubeUrl = new RegExp(urlPattern)
//        console.log($(this).val().match(youtubeUrl))
        if($(this).val().match(youtubeUrl)){
            $('#submitBtn').attr('disabled', false)
            $('#errorMsg').hide()
        }
        else $('#errorMsg').show() 
    });

});