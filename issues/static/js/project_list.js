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
            if (id == "sortable-projects")
            {
            $.ajax({
                url: PROJECT_SORT_URL,
                type: "POST",
                data: {'sorted_ids':sortedIDs,},
                success: function () {},
                error: function () { alert("error"); },
            });
            }
            else if (id == "sortable-users")
            {
            
            }
        }
    });
    $( ".sortable" ).disableSelection();
    
    $( '#new_project_button').click(function(e)
    {
        $('#new_project').slideDown();    
        $(this).slideUp();
    });

    $( '#new_project_cancel_button').click(function(e)
    {
        $('#new_project').slideUp();
        $('#new_project_button').slideDown();
    });

    $( "#new-project" ).submit(function(event)
    {       
        var slug = $("#id_slug").val();
        var project = $("#id_name").val();
        if (project == "")
        {
            $("#form_error").html("* Name cannot be blank.").show();
        }
        else if (slug == "")
        {
            $("#form_error").html("* Slug cannot be blank.").show();
        }
        else
        {
            $("#id_slug").val(URLify($("#id_slug").val()))
            $.post($(this).attr('action'), $(this).serialize(), function(data){
                if (data.status == "error")
                {
                    $("#form_error").html(data.message).show();
                }
                else if (data.status == "success")
                {
                    window.location.href = data.url;
                }
            });        
        }
        return false;
    });
    
    $(".project-tab").click(function(e)
    {
        //get the clicked id
        //$(this).id returns null here for some reason
        var target_id = event.target.id;
        
        //this determines which tab was clicked (pojects, in-progress, assigned, unassigned, needs-review, completed, or deleted)
        var tab = target_id.slice(9);
        
        //remove active tab
        $(".project-tab").each(function(i){
            $(this).removeClass("active");
        });
        
        //assign active tab
        $("#"+target_id).addClass("active");
        
        if (tab == "projects")
        {
            $("#project-issues").hide();
            $("#project-sort").show();
        }
        //show issues based on the tab clicked        
        else
        {
            $("#project-sort").hide();
            $("#project-issues").show();
            $(".project-issue").each(function(i){
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
    $(".collapse_issue, .expand_issue").click(function(e)
    {
        var degrees = 0;

        if ($(this).hasClass("collapse_issue"))
        { degrees = -90; }

        var child_list = $(this).siblings('.collapse-issue-list');               
        child_list.slideToggle();
        $(this).toggleClass("collapse_issue");
        $(this).toggleClass("expand_issue");

           $(this).css({
          '-webkit-transform' : 'rotate('+degrees+'deg)',
             '-moz-transform' : 'rotate('+degrees+'deg)',  
              '-ms-transform' : 'rotate('+degrees+'deg)',  
               '-o-transform' : 'rotate('+degrees+'deg)',  
                  'transform' : 'rotate('+degrees+'deg)',  
                       'zoom' : 1
            });


    });

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
        
        if (tab == "reorder")
        {
            $("#user-issues").hide();
            $("#user-sort").show();
        }
        //show issues based on the tab clicked        
        else
        {
            $("#user-sort").hide();
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

    $(document).ready(function() 
    {
        $('input[id="id_name"]').keyup( function() {
            var e = document.getElementById("id_slug");
            if (!e._changed) { 
                e.value = URLify(document.getElementById("id_name").value, 50); 
            }
        });
    });
});
