jQuery(function($) {

	$(".edit_tags .badge").on("click", function(event){
		event.preventDefault();
        event.stopPropagation();
        $("a.badge").removeClass("btn-success");
        $("a.badge").addClass("btn-info");
        $(this).removeClass("btn-info");
        $(this).addClass("btn-success");
        $("#tags").val($(this).text());
		$("a.btn").removeClass("disabled");
		$("#tags").attr("data-tag", $(this).attr("id"));
	});

    $('.tags').on('click', "#save_tag:not(.disabled)", function(event) {
        id = $("#tags").attr("data-tag");
        name = $("#tags").val();
        if (name.length == 0) {
            $("p.error-text").text("Tag name can not be empty.");
            $(".alert-error").show();
        } else {
            updateTag(id, name);
        }
    });

    $('.tags').on('click', "#delete_tag.disabled", function(event) {
        event.preventDefault();
        event.stopPropagation();
    });

    $('#delete_confirmation').on('click', "#delete_tag", function(event) {
        deleteTag($("#tags").attr("data-tag"));
    });

	function updateTag(id, name) {
        ajaxCall("/update_tag/" + id + "/" + name, function(result) { tagUpdated(result) });
    };

    function deleteTag(id) {
        ajaxCall("/delete_tag/" + id, function(result) { tagDeleted(result) });
    };

    function tagDeleted(data) {
        $("#"+data.id).remove();
        $("#tags").val('');
        $("a.btn").addClass("disabled");
        $("p.success-text").text("Tag " + data.name + " deleted!");
        $(".alert-success").show();
        $("#delete_confirmation").modal('hide');
    }

    function tagUpdated(data) {
        $("#"+data.id).text(data.name);
        $("#"+data.id).removeClass('btn-success');
        $("#"+data.id).addClass('btn-info');
        $("#tags").val('');
        $("a.btn").addClass("disabled");
        $("p.success-text").text("Tag " + data.name + " updated!");
        $(".alert-success").show();
    }

	function ajaxCall(target_url, onSuccess, onError) {
        $.ajax({
            url: target_url,
            type: 'POST',
            success: function(result) {
                onSuccess(result);
            },
            error: function(result) {
                if (typeof(onError) == 'undefined') {
                    $("p.error-text").text("Tag can not be updated. Try later.");
                    $(".alert-error").show();
                } else {
                    onError(result);
                }
            }
        });
    }

});