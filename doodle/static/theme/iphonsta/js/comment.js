$(function() {
	var $load_button = $('p.wp-pagenavi>a');
	var loading = false;
	var $commentlist = $('#commentlist>ol');
	var $comment = $('#comment');
	var allow_comment = $('#commentform').length;
	var next_cursor = '';
	var is_admin = typeof(comment_delete_url) != 'undefined';
	var comment_fetch_url = home_path + 'comment/json/'+ article_id + '/';
	var $bbcode = $('#bbcode');

	function generate_comment(comment) {
		var html = '<li class="comment"><div class="comment-info"><a id="comment-id-' + comment.id;
		if (comment.url) {
			html += '" href="' + comment.url;
		}
		html += '">' + comment.user_name + '</a> @' + comment.time;
		if (is_admin) {
			html += ' <a href="' + comment_delete_url + comment.id + '/">[删除]</a>';
		}
		html += ' <a href="#respond" class="comment-reply-link">[回复]</a></div><div>' + comment.content + '</div></li>';
		return html;
	}

	function bind_events_for_comment($html, id, user_name) {
		$html.find('a.comment-reply-link').click(function() {
			if (!allow_comment) {return;}
			var comment = $comment.val() + '[url=#comment-id-' + id + ']@' + user_name + '[/url]: ';
			$comment.focus().val(comment);
			$bbcode.attr('checked', true);
			return false;
		});
	}

	$load_button.click(function() {
		if (loading) {
			return false;
		}
		loading = true;
		var url = comment_fetch_url;
		if (next_cursor) {
			url += next_cursor;
		}

		$.getJSON(url, function(json) {
			next_cursor = json.next_cursor;
			if (!next_cursor) {
				$('div.comments').remove();
			} else {
				$load_button.text('载入下10条评论');
			}
			var comments = json.comments;
			var length = comments.length;
			if (length) {
				for (var index = 0; index < length; ++index) {
					var comment = comments[index];
					bind_events_for_comment($(generate_comment(comment)).appendTo($commentlist), comment.id, comment.user_name);
				}
			}
			loading = false;
		});
		_gaq.push(['_trackEvent', 'Comment', 'Load', article_id]);
		return false;
	});
});