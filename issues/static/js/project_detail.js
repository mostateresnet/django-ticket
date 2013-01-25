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
                error: function () { alert("error"); },
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
                        alert(data['errors']);
                        return false;
                    }
                    else{
                      $( '#issue-nr-'+issue_id ).remove();
                    }
                },
                error: function () { alert("error"); },
            });
        }
    });
	

	
    $(".tag").click(function(e)
    {    
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

});
