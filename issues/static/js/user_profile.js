$(function() 
{
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
    
    $( ".sortable" ).sortable({
        update: function( event, ui) {
            var id = (this).id
            var sortedIDs = $("#"+id).sortable("toArray");
            $.ajax({
                url: issue_sort_url, 
                type: "POST",
                data: {'sorted_ids':sortedIDs,},
                success: function () {  },
                error: function () { alert("error"); },
            });
        }
    });
    $( ".sortable" ).disableSelection();
    
    $(".user-tab").click(function(e)
    {
        //get the clicked id
        //$(this).id returns null here for some reason
        var target_id = event.target.id;
        
        //this determines which tab was clicked (pojects, in-progress, assigned, unassigned, needs-review, completed, or deleted)
        var tab = target_id.slice(6);
        
        //remove active tab
        $(".user-tab").each(function(i){
            $(this).removeClass("active");
        });
        
        //assign active tab
        $("#"+target_id).addClass("active");
        
        if (tab == "assigned")
        {
            $("#user-issues").hide();
            $("#sortable-assigned-issues").show();
        }
        //show issues based on the tab clicked        
        else
        {
            $("#sortable-assigned-issues").hide();
            $("#user-issues").show();
            $(".user-issue").each(function(i){
            if ($(this).hasClass(tab))
                {
                    $(this).show();
                }
                else
                {
                    $(this).hide();
                }
            });
        } 
    });
});