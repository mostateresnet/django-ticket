$(function() {   
    $( ".slide-title").click(function(e){
        $(this).siblings('.details').children('.details_drop').show();
        $(this).siblings('.details').slideToggle();
    });
});

