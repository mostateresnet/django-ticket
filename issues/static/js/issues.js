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

$(function() {

    function set_viewed_issue(issue, user)
    {
        $( "#new-notes-"+issue).remove();
        var url = UPDATE_ISSUE_URL + issue;
        $.ajax({
            url: url, 
            type: "post",
            data: "viewed=1",
            error: function () { alert("error"); },
        });

    }
    
    $( ".issue-title").click(function(e){
        $(this).siblings('.edit_drop').slideUp(function() 
        { 
            $(this).siblings('.details_drop').slideToggle(function()
            {
                if ($(this).is(":visible"))
                {
                    var id = $(this).attr('id')
                    var issue_id = parseInt(id.match(/^issue-details-(\d+)$/)[1]);    
                    //set_viewed_issue(issue_id, current_user);
                }
            }); 
        });
    });
    
    $( ".issue-nr-title").click(function(e){
        $(this).siblings('.details_drop').slideToggle(function()        
        {
            if ($(this).is(":visible"))
            {
                var id = $(this).attr('id');
                var issue_id = parseInt(id.match(/^issue-details-(\d+)$/)[1]);    
                set_viewed_issue(issue_id, current_user);
            }
        }); 
    });
    
    $( ".issue_edit").click(function(e){
        $(this).closest('.details_drop').slideUp(
        function() { $(this).closest('.details_drop').siblings('.edit_drop').slideDown(); } );      
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

        var post_action = $("#tag-container-" + tag_id).attr('data-tag-update-url') 
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

        var post_action = CREATE_TAG_URL;

        var default_color = "AAAAAA";
        var post_data = "label=" + new_tag_name + "&color=" + default_color;
        $('.new_tag_input').attr('value','');
       $.post(post_action, post_data, function(data)   
       {                 
            $("<style type='text/css'> .tag_" + data.id + " { background-color:#" + default_color + ";}</style>").appendTo("head");

            var new_element = new_tag_line.clone();

            new_element.attr('data-tag-update-url', data.url);    
            new_element.attr('id', "tag-container-" + data.id);    

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
		
		//processing for milestone here
		var milestone_date;
		if (pk_id) //if it is an edit
		{
			milestone_date = $("#id_"+pk_id+"-milestone").val();
			serial_data += "&milestone_date="+milestone_date;
		}
		else //if it is a new issue
		{
            milestone_date = $("#id_milestone").val();
			serial_data += "&milestone_date="+milestone_date
		}
		                  
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
    
    $( ".issue-delete" ).click(function(event){
        var targetid = event.target.id;
        var n=targetid.split("-");
        var issue_id=n[0];
        UPDATE_ISSUE_URL = $("#issue-details-" + issue_id).attr('data-issue-url');
        if( confirm("Are you sure you want to delete this issue?") )
        {
            $.post(
                    UPDATE_ISSUE_URL,
                    {'status': 'DL',},
                    function(data, textStatus, jqXHR) {
                        if (textStatus == "success"){
                            $( '#issue-'+issue_id ).remove();
                        }
                    });
        }
    });
    
    $( ".edit-issue-cancel-button" ).click(function(event)
    {
        $(this).closest('.edit_drop').slideUp();
    });
    
    $( ".issue_complete" ).click(function(event){
        var revision = window.confirm("Complete this issue?");
        if (revision) {
            var id = event.currentTarget.id;
            var issue_id = parseInt(id.match(/^close-(\d+)$/)[1]);
            //var url = window.location.pathname + issue_id
            UPDATE_ISSUE_URL = $("#issue-details-" + issue_id).attr('data-issue-url');
            
            $.post(
                UPDATE_ISSUE_URL,
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
        var issue_id=n[0];
        UPDATE_ISSUE_URL = $("#issue-details-" + issue_id).attr('data-issue-url');
        $.ajax({
            url: UPDATE_ISSUE_URL,
            type: "post",
            data: "status=IP",
            success: function() 
            { 
                $("#issue-" + issue_id).removeClass();
                $("#issue-" + issue_id).addClass("issue in-progress");
                $("#gravatar-" + issue_id).attr("src", "/static/img/clock.gif");
            },
            error: function () { alert("error"); },
        });
    });
    $( ".issue_add_commit" ).click(function(event){
        var revision = window.prompt("Enter the revision number below:","");
        if (revision) {
            var id = event.currentTarget.id;
            var issue_id = parseInt(id.match(/^add-commit-(\d+)$/)[1]);
            CREATE_COMMIT_URL = $("#issue-details-" + issue_id).attr('data-commit-url')
            $.ajax({
                url: CREATE_COMMIT_URL,
                type: "post",
                data: {'revision': revision, 'issue': issue_id },
                success: function(data) 
                {       
                    if ('errors' in data)
                    {
                        alert("error");
                        return;
                    }      
                    $("#commit-header-" + issue_id).removeClass("hidden");

                    var newCommit;
                    if ('url' in data)
                    { newCommit = $("<li> <a href=\"" + data['url'] + "\" target=\"_blank\">" + revision + "</a> &emsp; on " + data['datetime'] + "</li>"); }                    
                    else 
                    { newCommit = $("<li>" + revision + " &emsp; on " + data['datetime'] + "</li>"); }

                    $("#commit-list-" + issue_id).append(newCommit);
                },
                error: function () { alert("error"); },
            });

  
        }
    });

    $( ".issue_add_note" ).click(function(event)
    {
            var id = event.currentTarget.id;
            var issue_id = parseInt(id.match(/^add-note-(\d+)$/)[1]);

            postNote('', issue_id);
    });
    
    function postNote(prepend, issue_id)
    {
        var note = window.prompt("Add Note:","");
        if (note) 
        {           
            CREATE_NOTE_URL = $("#issue-details-" + issue_id).attr('data-note-url')
            $.ajax({
                url:  CREATE_NOTE_URL,
                type: "post",
                data: {'label': prepend + note, 'issue': issue_id, 'creator': current_user },
                success: function(data) 
                {
                    if ('errors' in data)
                    {
                        alert("error");
                        return false;
                    }

                    $("#note-header-" + issue_id).removeClass("hidden");

                    var newNote = $("<div class = \"note\"> " + current_user_name + " on " + data['datetime'] + 
                    "</br>&emsp;"  + prepend + note + "</div>");

                    $("#note-list-" + issue_id).append(newNote);
                },
                error: function () { alert("error"); },
            });
            return true;
        }
        return false;
    }
    
    var date = new Date();
	
	//initializes all datepickers
	$( ".milestone-datepicker").datepicker({ 
		dateFormat: 'yy-mm-dd',
        minDate: '0',
		beforeShowDay: function(date) {
            var m = ('0' + (date.getMonth()+1)).slice(-2);
            var d = date.getDate(), y = date.getFullYear();
            d=String(d);
            if (d.length ==1)
            {
                d="0"+d            
            }
			for (i = 0; i < milestone_dates.length; i++) {
				if($.inArray(y + '-' + m + '-' + d,milestone_dates) != -1) {
					//return [false];
					return [true, 'ui-state-active', ''];
				}
			}
			return [true];

		}
	});
    
});