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
            $.post(
                SORT_ISSUE_URL,
                issue_priority,
                function(data, textStatus, jqXHR) {
                    if (data != "success"){
                        location.reload(true);
                    }
                });
        }
    });



    
    
    $('#issue_filter').change(function(e)
    {
        var url = $(this).attr('data-pj') + "/";
        if ($(this).attr('value') != "ALL")
        { url+="filter/" + $(this).attr('value'); }
        window.location.pathname = url;
    });



    $( "#new-issue-button" ).click(function(event){
        $(" #new-issue ").slideDown();
    });
    $( "#new-issue-cancel-button" ).click(function(event){
        $(" #new-issue ").slideUp();
    });

    $( ".handle" ).disableSelection();


    $( ".issue_reject").click(function(e)
     {
            var target = event.target;
            var n=target.id.split("-");
            var issue_id=n[0];
            UPDATE_ISSUE_URL = $("#issue-details-" + issue_id).attr('data-issue-url');

           if (postNote('REJECTED: ', issue_id))
           {
            $.ajax({
                url: UPDATE_ISSUE_URL,
                type: "post",
                data: "status=AS",
                error: function () { alert("ERROR: There has been an error in your post request."); },
            });

            window.location.reload(true);
           }

    });



    $( ".issue_approve").click(function(e)
     {
        var confirm = window.confirm("Approve this issue?");
        if (confirm)
        {
            var target = event.target;
            var n=target.id.split("-");
            var issue_id=n[0];
            UPDATE_ISSUE_URL = $("#issue-details-" + issue_id).attr('data-issue-url');
            $.ajax({
                url: UPDATE_ISSUE_URL,
                type: "post",
                data: "status=CP&approved_by="+current_user,
                success: function(data)
                {
                    if ('errors' in data)
                    {
                        alert("ERROR: "+data.errors);
                        return false;
                    }
                    else{
                      $( '#issue-nr-'+issue_id ).remove();
                    }
                },
                error: function () { alert("ERROR: There has been an error in your post request."); },
            });
        }
    });
	

	
    $(".tag").click(function(e)
    {            
        if ($(this).hasClass('tag_mod'))
        { return true; }

        $($(this).attr('class').split(' ')).each(function() 
        { 
            if (/tag_\d+/.test(this))
            {              
                var tag_id = this.match(/^tag_(\d+)$/)[1];  
                if (e.ctrlKey)
                {
                    var params = location.search.substr(1).split("&");
                    for (var i = 0; i < params.length; i++)
                    {
                        var props = params[i].split("=");                        
                        if (props.length > 1 && props[0].toLowerCase() == "tag")
                        {
                            tag_id+= "," + props[1];                            
                            break;
                        }
                    }
                }                

                var id_array = tag_id.split(",");

                id_array = $.grep(id_array, function(v, k)
                {
                    return $.inArray(v ,id_array) === k;
                });
               
                window.location.href = "?tag=" + id_array.join();
                return false;
            }    
        });
    });

    $(".tag_remove").live("click", function(e)
    {
        $(this).parent().hide("puff", {}, 500, function()
        { $(this).remove(); });
        //e.stopPropagation();
        return false;
    });

    $('.tag_field').keydown(function(e) 
    {
        var tag_name = $(this).val().toLowerCase()
        var issue_pk = $(this).attr('data-pk');
        // We need to ignore a few characters that will break the html....

        if (e.which == 32 || e.which == 13) // Spacebar
        {
            // Check to see if a tag with this name already exists
            // if so, use its pk, if not, create it, and use that pk
            var used_tag = ($("#tag-data-" + issue_pk + "-" + tag_name).length > 0);
            if (!used_tag) 
            { $(this).val(''); }

            if (tag_name != "")
            {
                // Need to check if this tag is already present
                var tag_pk = 0;            
                
                $.ajax({
                    url: SEARCH_TAG_URL,
                    type: "get",
                    data: "label=" + tag_name,
                    success: function(data)
                    {
                        if ('pk' in data)
                        {  
                            tag_name = data['label'];
                            tag_pk = data['pk'];
                        }


                        var parent = $("#tag-list-"+issue_pk);

                        // Does this tag addition already exist?
                       
                        if (!used_tag)                    
                        {
                            var tag_detail;
                            if (tag_pk > 0)
                            { 
                                tag_detail = 
                                    $("<span id=\"tag-data-" + issue_pk + "-" + tag_name.toLowerCase() + 
                                    "\" data-pk=\"" + tag_pk + "\" class=\"left tag_mod tag tag_" + tag_pk + "\">" + tag_name + 
                                    " <div class = \"tag_remove\"/></span>"
                                    );
                            }
                            else 
                            { 
                                tag_detail = 
                                    $("<span id=\"tag-data-" + issue_pk + "-" + tag_name.toLowerCase() + 
                                    "\" class=\"left tag_mod tag\" style=\"background-color:#AAAAAA;\">" + tag_name + 
                                    " <div class = \"tag_remove\"/></span>"
                                    );
                            }

                            parent.append(tag_detail);
                        }

                    },
                });

            }

            e.preventDefault();
            return false;
        }
    });

});
