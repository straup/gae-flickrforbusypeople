if (! info){
    var info = {};
}

if (! info.aaronland){
    info.aaronland = {};
}

if (! info.aaronland.ffbp){
    info.aaronland.ffbp = {};
}

info.aaronland.ffbp.Photos = function(args){
    this.args = args;
};

// do the thing to inherit from info.aaronland.flickrapp.API here (see below) ...

info.aaronland.ffbp.Photos.prototype.show_photos = function(nsid, offset, duration){

	$("#ffbp_status").html();
  	$("#ffbp_status").hide();

	var hex = hex_md5(nsid);
	var short_hex = hex.substring(0, 6);

        var uid = "thumbs_" + hex;

  	var status_id = "status_" + duration;

  	var container = "#slice_thumbs_" + duration;

  	var buddy_icon = $("#buddy_" + hex)[0].src;

  	var kids = $(container).children();

	if (kids.length){
		for (var i=0; i < kids.length; i++){
  			var child = kids[i];
  			var id = child.getAttribute("id");
  			var el = $("#" + id);

                        // console.log('uid: ' + uid + ' id: ' + id + ' css: ' + el.css('display'));
 
			if ((id == uid) && (el.css('display') == 'none')){
				el.show();

				// $("#count_" + uid).css('border', '2px solid #' + short_hex);
                                continue;
			}

			// $("#count_" + id).css('border', 'none');
			el.hide();
		}
	}

	if ($("#" + uid).length){
		return;                                  
	}
                                  
  	var api_args = {
		'host' : this.args['host'],
  	};

  	var search_args = {
		'user_id' : nsid,
  		'min_upload_date' : offset,
  		'format' : 'json',
  		'crumb' : this.args['crumb'],
  	};

        // see above inre: inheritance...

  	var api = new info.aaronland.flickrapp.API(api_args)

  	api.api_call('search', search_args, function (rsp){

		$("#" + status_id).html();
  		$("#" + status_id).hide();

                $("#buddy_" + hex)[0].src = buddy_icon;

  		var short_hex = hex.substring(0, 6);
  		var html = '';

  		if (rsp.photos.photo.length == 0){
		        $("#" + status_id).html("Foiled again! The Flickr API returns no photos for that user.");
  		        $("#" + status_id).show();
                        return;
  		}

		var html = '<div id="' + uid + '">';
		html += '<div class="slice_thumbs_from">';
		html += 'From <a href="http://www.flickr.com/photos/' + nsid + '" target="_flickr">' + rsp['photos']['photo'][0]['ownername'] + '</a>:';
		html += '</div>';
                                  
  		for (i in rsp.photos.photo){
  			var ph = rsp.photos.photo[i];

                        var sz = 75;

  			var link = 'http://www.flickr.com/photos/' + ph['owner'] + '/' + ph['id'];
  			var src = 'http://farm' + ph['farm'] + '.static.flickr.com/' + ph['server'] + '/' + ph['id'] + '_' + ph['secret'] + '_s.jpg';

  			var img = '<a href="' + link + '" target="_fl' + ph['id'] + '">';
                        img += '<img src="' + src + '" height="' + sz + '" width="' + sz + '" style="border:3px solid #' + short_hex + ';" />';
                        img += '</a>';

  			html += '<div id="thumb_' + ph['id'] + '" class="slice_thumb_hex">';
                        html += img;
                        html += '<div class="slice_thumb_title">' + ph['title'].substring(0, 6) + '...</div>';
                        html += '</div>';
  		}

		html += '</div>';
		$(container).append(html);

		// $("#count_" + uid).css('border', '2px solid #' + short_hex);

  	}, function (rsp) {

                $("#buddy_" + hex)[0].src = buddy_icon;

		$("#" + status_id).html('Unable to retrieve any photos for that user. The attempt failed with the following message:<br /><br />' + rsp.error.message);
		$("#" + status_id).show();
		return;
  	});

        $("#buddy_" + hex)[0].src = "/images/loading.gif";
                              
	$("#" + status_id).html("Retrieving photos...");
  	$("#" + status_id).show();
};
