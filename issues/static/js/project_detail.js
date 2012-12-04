// Prevents CSRF for AJAX
$('html').ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        // Only send the token to relative URLs i.e. locally.
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

$(function() {
    $( ".simple_overlay").dblclick(function(e){
        $(e.currentTarget).find('.details-form').show();
        $(e.currentTarget).find('.details').hide();
    });

    $( ".issue-title").click(function(e){
        $(this).siblings('.edit_drop').slideUp(
        function() { $(this).siblings('.details_drop').slideToggle(); } );      
    });

    $( ".issue_edit").click(function(e){
        $(this).closest('.details_drop').slideUp(
        function() { $(this).closest('.details_drop').siblings('.edit_drop').slideDown(); } );      
    });

    $( ".issue-list" ).sortable({
        // revert: true,
        distance: 5,
        axis: 'y',
        handle: '.handle',
        stop: function(event, ui) {
            var issues = $(event.target).find( '.issue' );
            var issue_priority = {};
            issues.each(function(index, Element){
                var id = Element.id;
                var issue_id = parseInt(id.match(/^issue-(\d+)$/)[1]);
                issue_priority[issue_id] = (issues.length - index - 1);
            });
            var url = window.location.pathname + "sort"
            $.post(
                url,
                issue_priority,
                function(data, textStatus, jqXHR) {
                    if (data != "success"){
                        location.reload(true);
                    }
                });
        }
    });


    $( ".new_tag").click(function(e)
    {
        var new_tag_name = $(this).siblings('.new_tag_input').attr('value');
        var post_action = window.location.pathname + "tags/";
        var default_color = "AAAAAA";
        var post_data = "label=" + new_tag_name + "&color=" + default_color;
        $('.new_tag_input').attr('value','');
       $.post(post_action, post_data, function(data)   
       {                 
            var new_element = new_tag_line.clone();
            new_element.find('.tag_label').text(new_tag_name);
            new_element.find('.tag_mod').css('background-color',"#" + default_color);
            new_element.find('.tag_check').attr('id', 'tagchk_' + data.id);
            $('.add_tag_area').before(new_element);
        } );
    });


    $( ".edit_form, #new-issue" ).submit(function(event)
    {       
        // Intercept the post data and append
        // our custom tags.
        var serial_data = $(this).serialize();

        var pk_str = $(this).attr('id');
        var pk_id = pk_str.match(/\d+/);
        var append_str = "";

        $(this).find(".tag_editor input:checked").each(function()
        {
            var i = $(this).attr('id');
            var chk_id = i.match(/\d+/);
            if (pk_id)
            { append_str += "&" + pk_id + "-tags=" + chk_id;  }
            else
            { append_str += "&tags=" + chk_id;  }
        });

        serial_data += append_str;
        $.post($(this).attr('action'), serial_data, function(){window.location.reload(true);});
        
        return false;
    });

    $( "#new-issue-button" ).click(function(event){
        $(" #new-issue ").slideDown();
    });
    $( "#new-issue-cancel-button" ).click(function(event){
        $(" #new-issue ").slideUp();
    });
    $( "#edit-issue-cancel-button" ).click(function(event)
    {
        $(this).closest('.edit_drop').slideUp();
    });
    $( ".handle" ).disableSelection();
    $( ".close-button" ).click(function(event){
        var revision = window.prompt("Closed by which revision?","");
        if (revision) {
            var id = event.currentTarget.id;
            var issue_id = parseInt(id.match(/^close-(\d+)$/)[1]);
            var url = window.location.pathname + issue_id
            $.post(
                url,
                {'closed_by_revision': revision},
                function(data, textStatus, jqXHR) {
                    if (textStatus == "success"){
                        $( '#issue-'+issue_id ).remove();
                    }
                });
        }
    });
});
