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

    this.contacts_seen = {};
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

			if ((id == uid) && (el.css('display') == 'none')){
				el.show();
                                continue;
			}

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
  		'crumb' : this.args['search_crumb'],
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

                var embiggen = rsp.embiggen;
		var mobile = rsp.mobile;

                var count = parseInt(rsp.photos.total);

                if ((embiggen) && (count > 20)){
                    embiggen = 0;

                    html += '<div class="donot_embiggen">Embiggen-ing has been disabled for ' + rsp['photos']['photo'][0]['ownername'] + '\' photos, this time, because there are way too many of them to display at once. It\'s probably a job best handled by <a href="http://www.flickr.com/photos/' + rsp['photos']['photo'][0]['owner'] + '" target="_flickr">their Flickr photostream</a>.</div>';
                }

  		for (i in rsp.photos.photo){
  			var ph = rsp.photos.photo[i];

                        var sz = 75;

  			var link = 'http://www.flickr.com/photos/' + ph['owner'] + '/' + ph['id'];
  			var src = 'http://farm' + ph['farm'] + '.static.flickr.com/' + ph['server'] + '/' + ph['id'] + '_' + ph['secret'] + '_s.jpg';

                        if (embiggen){
                            src = 'http://farm' + ph['farm'] + '.static.flickr.com/' + ph['server'] + '/' + ph['id'] + '_' + ph['secret']

				if (mobile){
				    src += '_m';
				}

			    src += '.jpg';
                        }

  			var img = '<a href="' + link + '" target="_fl' + ph['id'] + '">';

                        if (embiggen){
                            img += '<img src="' + src + '" style="border:4px solid #' + short_hex + ';" />';
                        }

                        else {
                            img += '<img src="' + src + '" height="' + sz + '" width="' + sz + '" style="border:3px solid #' + short_hex + ';" />';
                        }

                        img += '</a>';

  			html += '<div id="thumb_' + ph['id'] + '" class="slice_thumb_hex">';
                        html += img;

                        if (embiggen){
                            html += '<div class="slice_thumb_title">' + ph['title'] + '...</div>';
                        }

                        else {
                            html += '<div class="slice_thumb_title">' + ph['title'].substring(0, 6) + '...</div>';
                        }

                        html += '</div>';
  		}

		html += '</div>';
		$(container).append(html);

                if (duration == '8h'){
                	window.location.href = "#slice_" + duration;
		}

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

info.aaronland.ffbp.Photos.prototype.fetch_contacts = function(offset){

    var _self = this;

    var doThisOnSuccess = function(rsp){

        var count = parseInt(rsp['count']);

        if (! count){
            $("#slice_noone_" + offset).html("Nothing new...");
            return;
        }

        var html = '';
        var contacts = 0;

        for (var i=0; i < count; i++){

            var contact = rsp['contacts'][i];
            var nsid = contact['nsid'];

            if (_self['contacts_seen'][nsid]){
                continue;
            }

            _self['contacts_seen'][nsid] = rsp['offset'];
            contacts += 1;

            html += '<div id="photos_' + contact['nsid_hex'] + '" class="photos_hex">';

            html += '<a href="#" onclick="window.ffbp.show_photos(\'' + contact['nsid'] + '\', \'' + rsp['offset'] + '\', \'' + rsp['duration'] + '\');return false;" title="yay! new photos from ' + contact['username'] + '">';
            html += '<img id="buddy_' + contact['nsid_hex'] + '" src="' + contact['buddyicon'] + '" height="48" width="48" class="buddy_hex" style="border:3px solid #' + contact['nsid_short_hex'] + ';" alt="' + contact['username'] + '" />';
            html += '</a>';

            html += '<div id="count_thumbs_' + contact['nsid_hex'] + '" class="count_thumbs_hex">';
            html += '<a href="http://www.flickr.com/photos/' + contact['nsid'] + '" target="' + contact['nsid_hex'] + '">';

            if (parseInt(contact['count']) == 1){
                html += '<strong>1</strong> photo';
            }

            else {
                html += '<strong>' + contact['count'] + '</strong> photos';
            }

            html += '</a>';
            html += '</div>';
            html += '</div>';
        }

        if (! contacts){
            $("#slice_noone_" + offset).html("Nothing new...");
            return;
        }

        html += '<br clear="all" />';

        html += '<div class="status" id="status_' + rsp['duration'] + '"></div>';
        html += '<div class="slice_thumbs" id="slice_thumbs_' + rsp['duration'] + '"></div>';
        html += '<br clear="all" />';

        $("#slice_" + offset).html(html);
    };

    var doThisIfNot = function(rsp){

        var html = '';

        html += '<span style="font-size:small;">';
        html += 'I give up! The magic future-world we keep dreaming of says: <em>' + rsp['error']['message'] + '</em>';
        html += '</span>';

        $("#slice_noone_" + offset).html(html);
        return;
    };

    var api_args = {
        'host' : this.args['host'],
    };

    var search_args = {
        'offset' : offset,
        'format' : 'json',
        'crumb' : this.args['contacts_crumb'],
    };

    // Note: We are calling the ffbp API rather than the Flickr API
    // directly. This may need to be revisited in light of token/sig
    // stuff. I suppose on possibility would be to have an endpoint
    // that simply generated a sig when passed a bunch of API args
    // and a (very) time-sensitive crumb. That might work for queries
    // that are implicity scoped by time but I haven't thought it all
    // through yet... (20091107/asc)

    var api = new info.aaronland.flickrapp.API(api_args)
    api.api_call('contacts', search_args, doThisOnSuccess, doThisIfNot);
};

info.aaronland.ffbp.Photos.prototype.show_photos_inline = function(nsid, offset, duration){

	$("#ffbp_status").html();
  	$("#ffbp_status").hide();

	var hex = hex_md5(nsid);
	var short_hex = hex.substring(0, 6);

        var uid = "photos_" + hex;

  	var status_id = "status_" + duration;
  	var buddy_icon = $("#buddy_" + hex)[0].src;

  	thumbs = $('[class=slice_thumb_' + hex + ']');

  	if (thumbs.length){

  		for (i=0; i < thumbs.length; i++){
  			var id = thumbs[i].getAttribute('id');
                        var el = $("#" + id);

  		        if (el.css('display') == 'block'){
  			      el.hide();
                              continue;
  		        }

                        el.show();
                }

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

  		if (rsp.photos.photo.length == 0){
		        $("#" + status_id).html("Foiled again! The Flickr API returns no photos for that user.");
  		        $("#" + status_id).show();
                        return;
  		}

                var ctx = $("#photos_" + hex);

  		for (i in rsp.photos.photo){
  			var ph = rsp.photos.photo[i];
                        var sz = 48;

  			var link = 'http://www.flickr.com/photos/' + ph['owner'] + '/' + ph['id'];
  			var src = 'http://farm' + ph['farm'] + '.static.flickr.com/' + ph['server'] + '/' + ph['id'] + '_' + ph['secret'] + '_s.jpg';

  			var img = '<a href="' + link + '" target="_fl' + ph['id'] + '">';
                        img += '<img src="' + src + '" height="' + sz + '" width="' + sz + '" style="border:3px solid #' + short_hex + ';" />';
                        img += '</a>';

  			var html = '<div id="thumb_' + ph['id'] + '" class="slice_thumb_' + hex + '" style="float:left;margin-right:10px;margin-bottom:10px;">';
                        html += img;
                        html += '<div class="slice_thumb_title">' + ph['title'].substring(0, 6) + '...</div>';
                        html += '</div>';

                        ctx.after(html);
                        ctx = $("#thumb_" + ph['id']);
  		}


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