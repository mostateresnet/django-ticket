$(function() 
{
    $( '#new_project_button').click(function(e)
    {
        $('#new_project').slideDown();      
    });

    $( '#new_project_cancel_button').click(function(e)
    {
        $('#new_project').slideUp();      
    });

    $( "#new-project" ).submit(function(event)
    {       
        $.post($(this).attr('action'), $(this).serialize(), function(){window.location.reload(true);});        
        return false;
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
