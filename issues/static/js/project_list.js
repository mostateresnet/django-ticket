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
