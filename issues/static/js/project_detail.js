// Prevents CSRF for AJAX

var colors = 
[
    '444444', '5A5A5A', '6F6F6F', '777777', '888888', 'AAAAAA', 'CCCCCC', 'EEEEEE', 'FFFFFF',
    '440000', '5A0000', '6F0000', '770000', '880000', 'AA0000', 'CC0000', 'EE0000', 'FF0000',
    '004400', '005A00', '006F00', '007700', '008800', '00AA00', '00CC00', '00EE00', '00FF00',
    '000044', '00005A', '00006F', '000077', '000088', '0000AA', '0000CC', '0000EE', '0000FF',
    '444400', '5A5A00', '6F6F00', '777700', '888800', 'AAAA00', 'CCCC00', 'EEEE00', 'FFFF00',
    '442200', '5A2D00', '6F3800', '773C00', '884400', 'AA5500', 'CC6600', 'EE7700', 'FF8800',
    '004444', '005A5A', '006F6F', '007777', '008888', '00AAAA', '00CCCC', '00EEEE', '00FFFF',
    '440044', '5A005A', '6F006F', '770077', '880088', 'AA00AA', 'CC00CC', 'EE00EE', 'FF00FF'
];

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
    $( ".issue-title").click(function(e){
        $(this).siblings('.edit_drop').slideUp(
        function() { $(this).siblings('.details_drop').slideToggle(); } );      
    });

    $( ".issue-nr-title").click(function(e){
        $(this).siblings('.details_drop').slideToggle();
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

    $('.new_tag_input').keypress(function (e) 
    {
        if (e.which == 13) 
        {
            e.preventDefault();
            return false;
        }
    });

    $(document).click(function(e)
    {
        if($(e.target || e.srcElement).closest('#color_selector').length == 0)
        { $("#color_selector").hide('slow'); }
    });

    $( ".tag_mod").live('click',function(e)
    {
        var pos = $(this).offset();
        var clr_selector = $('#color_selector');
        clr_selector.css('left',pos.left - 2 + 'px');
        clr_selector.css('top',pos.top + 16 + 'px');
        clr_selector.attr('data-cls',$(this).attr('data-cls'));
        clr_selector.show('slow');

    });

    $(".color_spot").live('click',function(e)
    {
        $("#color_selector").attr('data-sel', $(this).attr('data-sel'));

        var tag_id = $("#color_selector").attr('data-cls');
        var color_id = $("#color_selector").attr('data-sel');
        var new_color = colors[color_id];

        $(".tag_" + tag_id).css('background-color', '#' + new_color);
        $( "#color_selector").hide('slow');

        var existing_label = $(".tag_mod.tag_" + tag_id + ":first").siblings('.tag_label').text();

        var post_action = window.location.pathname + "tags/" + tag_id;
        var post_data = "label=" + existing_label + "&color=" + new_color;
        $.post(post_action, post_data);

    });

    $(".color_spot").live('hover',function(e)
    {
        var color_id = $(this).attr('data-sel');
        var new_color = colors[color_id];
        $("#color_input").attr('value',new_color);
    });


    $("#color_hex_button").click(function(e)
    {
        var tag_id = $("#color_selector").attr('data-cls');
        var new_color = $("#color_input").attr('value');

        $(".tag_" + tag_id).css('background-color', '#' + new_color);
        $( "#color_selector").hide('slow');

        var existing_label = $(".tag_mod.tag_" + tag_id + ":first").siblings('.tag_label').text();

        var post_action = window.location.pathname + "tags/" + tag_id;
        var post_data = "label=" + existing_label + "&color=" + new_color;
        $.post(post_action, post_data);
    });

    $( "#color_selector").ready(function(e)
    {
        for (x in colors)
        {
            var clr = $("<div class=\"color_spot\" data-sel=\""+ x +"\"></div>");
            clr.css('background-color',"#" + colors[x]);           
            $("#color_palette").append(clr);
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
            $("<style type='text/css'> .tag_" + data.id + " { background-color:#" + default_color + ";}</style>").appendTo("head");

            var new_element = new_tag_line.clone();
            var tag_mod = new_element.find('.tag_mod');
            tag_mod.removeClass("tag_"); // Left over from the clone...
            tag_mod.addClass('tag_'+ data.id);
            tag_mod.attr('data-cls', data.id);    
            new_element.find('.tag_label').text(new_tag_name);
            new_element.find('.tag_check').attr('id', 'tagchk_' + data.id);
        
            $('.add_tag_area').before(new_element);
        } );
    });


    $( ".edit_form, #new-issue" ).submit(function(event)
    {       
        // Intercept the post data and append
        // our custom tags.
        var $this = $(this);
        var serial_data = $this.serialize();

        var pk_str = $this.attr('id');
        var pk_id = pk_str.match(/\d+/);
        var append_str = "";

        $this.find(".tag_editor input:checked").each(function()
        {
            var i = $(this).attr('id');
            var chk_id = i.match(/\d+/);
            if (pk_id)
            { append_str += "&" + pk_id + "-tags=" + chk_id;  }
            else
            { append_str += "&tags=" + chk_id;  }
        });
        
        serial_data += append_str;
        $.post($this.attr('action'), serial_data, function(data)
        {
            $this.find("p.errors").toggleClass("errors", false)

            if (data.status == "error")
            {
                if(pk_id)
                {
                    for (var key in data.errors)
                    {
                        $("#id_"+pk_id+"-"+key).closest("p").toggleClass("errors", true)
                    }
                }
                else
                {
                    for (var key in data.errors)
                    {
                        $("#id_"+key).closest("p").toggleClass("errors", true)
                    }
                }
                return false;
            }
            else
            {
                window.location.reload(true);
            }
        });
        
        return false;
    });
    
    $('#issue_filter').change(function(e)
    {
        var url = $(this).attr('data-pj') + "/";
        if ($(this).attr('value') != "ALL")
        { url+="filter/" + $(this).attr('value'); }
        window.location.pathname = url;
    });

    $( ".issue-delete" ).click(function(event){
        var targetid = event.target.id;
        var n=targetid.split("-");
        var issueid=n[0];
        var url = window.location.pathname + issueid
        if( confirm("Are you sure you want to delete this issue?") )
        {
            $.post(
                    url,
                    {'status': 'DL',},
                    function(data, textStatus, jqXHR) {
                        if (textStatus == "success"){
                            $( '#issue-'+issueid ).remove();
                        }
                    });
        }
    });

    $( "#new-issue-button" ).click(function(event){
        $(" #new-issue ").slideDown();
    });
    $( "#new-issue-cancel-button" ).click(function(event){
        $(" #new-issue ").slideUp();
    });
    $( ".edit-issue-cancel-button" ).click(function(event)
    {
        $(this).closest('.edit_drop').slideUp();
    });
    $( ".handle" ).disableSelection();
    $( ".issue_complete" ).click(function(event){
        var revision = window.confirm("Complete this issue?");
        if (revision) {
            var id = event.currentTarget.id;
            var issue_id = parseInt(id.match(/^close-(\d+)$/)[1]);
            var url = window.location.pathname + issue_id
            
            $.post(
                url,
                {'status':'NR',},
                function(data, textStatus, jqXHR) {
                    if (textStatus == "success"){
                        $( '#issue-'+issue_id ).remove();
                    }
                });
        }
    });
    $( ".issue_work_on").click(function(e){
        var target = event.target;
        var n=target.id.split("-");
        var issueid=n[0];
        $.ajax({
            url: "/"+project_slug+"/"+issueid,
            type: "post",
            data: "status=IP",
            success: function() { 
                document.getElementById(target.parentNode.parentNode.id).className="issue in-progress";
            },
            error: function () { alert("error"); },
        });
    });
    $( ".issue_add_commit" ).click(function(event){
        var revision = window.prompt("Enter the revision number below:","");
        if (revision) {
            var id = event.currentTarget.id;
            var issue_id = parseInt(id.match(/^add-commit-(\d+)$/)[1]);
            
            $.ajax({
                url:  "/"+project_slug+"/"+"createcommit/",
                type: "post",
                data: {'revision': revision, 'issue': issue_id,},
                success: function() { 
                    window.location.reload(true);
                },
                error: function () { alert("error"); },
            });
        }
    });

    $( ".issue_reject").click(function(e)
     {
        var target = event.target;
        var n=target.id.split("-");
        var issueid=n[0];
        $.ajax({
            url: "/"+project_slug+"/"+issueid,
            type: "post",
            data: "status=AS",
            error: function () { alert("error"); },
        });
       window.location.reload(true);
    });

    $( ".issue_approve").click(function(e)
     {
        var target = event.target;
        var n=target.id.split("-");
        var issueid=n[0];
        $.ajax({
            url: "/"+project_slug+"/"+issueid,
            type: "post",
            data: "status=CP",
            error: function () { alert("error"); },
        });
       window.location.reload(true);
    });
});
