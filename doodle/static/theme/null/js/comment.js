$(function() {
	var $window = $(window);
	var complete = false;
	var loading = true;
	var lastScrollTop = 0;
	var $commentlist = $('#commentlist>ol');
	var $comment = $('#comment');
	var $temp = $('<ol/>');
	var $comment_float_list = $('<ol class="commentlist comment-float-list"/>').appendTo(document.body).hide();
	var $commentform = $('#commentform');
	var allow_comment = $commentform.length;
	var page = 1;
	var comment_order = true;
	var $comment_order_asc = $('#comment-order-asc');
	var $comment_order_desc = $('#comment-order-desc');
	var is_admin = typeof(comment_delete_url) != 'undefined';
	var $del_comment_button = $('<span id="del-comment-button">确认删除</span>');
	var comment_fetch_url = home_path + 'article/'+ article_id + '/comments/';
	var $more_hint = $('#more-hint');
	var $respond = $('#respond');
	var $wap = $('a[href="/wap/?mobile=1"]');

	if ($wap.length) {
		$wap[0].href = '/wap' + location.pathname + '?mobile=1';
	}

	function generate_comment(comment) {
		var html = '<li><p class="comment-author"><img src="';
		html += comment.img;
		html += '?s=48&amp;d=monsterid" class="avatar" height="48" width="48"/><cite><a id="comment-id-';
		html += comment.id;
		if (comment.url) {
			html += '" href="';
			html += comment.url;
		}
		html += '">';
		html += comment.user_name;
		html += '</a></cite>';
		var uas = comment.ua;
		if (uas) {
			html += '<span class="ua">';
			for (var i = 0, ua; i < uas.length; ++ i) {
				ua = comment.ua[i];
				html += '<img src="/static/img/ua/';
				html += ua.replace(/ /g, '-');
				html += '.png" alt="';
				html += ua;
				html += '" title="';
				html += ua;
				html += '"/>';
			}
			html += '</span>';
		}
		html += '<br/><small><strong>';
		html += comment.time;
		html += '</strong>';
		if (is_admin) {
			html += ' <span class="edit-user"><a href="';
			html += user_edit_url;
			html += comment.id;
			html += '/">[用户设定]</a></span> <span class="edit-comment"><a href="';
			html += comment_edit_url;
			html += comment.id;
			html += '/">[编辑]</a></span> <span class="del-comment">[删除]</span>';
		}
		html += '</small></p><div class="commententry" id="commententry-';
		html += comment.id;
		html += '"><div>';
		html += comment.content;
		html += '</div></div><a class="comment-reply-link" href="#respond">回复</a></li>';
		return html;
	}

	function bind_events_for_comment($html, id, user_name) {
		$html.find('a.comment-reply-link').click(function() {
			reply(id, user_name);
		});
		$html.find('a[href^="#comment-id-"]').hover(function(ev) {
			var comment_author_id = $(this).attr('href').substr(12);
			var ref_comment_link = $commentlist.find('#comment-id-' + comment_author_id);
			if (ref_comment_link.length) {
				$comment_float_list.css({
					'top': ev.pageY,
					'left': ev.pageX + 50
				}).append(ref_comment_link.parent().parent().parent().clone().find('a.comment-reply-link').remove().end()).fadeTo(1000, 0.9);
			}
		}, function() {
			$comment_float_list.hide().empty();
		});
		$html.find('pre>code').each(function(i, e) {hljs.highlightBlock(e)});
		if (is_admin) {
			$html.find('span.del-comment').data('id', id).hover(function(){
				$(this).append($del_comment_button);
			}, function(){
				$del_comment_button.detach();
			});
		}
	}

	function get_comment() {
		var url = comment_fetch_url;
		if (comment_order) {
			url += 'asc/';
		} else {
			url += 'desc/';
		}
		url += page;

		$.ajax({
			'url': url,
			'dataType': 'json',
			'error': function(jqXHR, textStatus){
				if (textStatus == 'timeout') {
					get_comment();
				}
			},
			'success': function(json){
				var next_page = json.next_page;
				if (next_page) {
					page = next_page;
					$more_hint.show();
				} else {
					complete = true;
					$more_hint.hide();
				}
				var comments = json.comments;
				var length = comments.length;
				if (length) {
					for (var index = 0; index < length; ++index) {
						var comment = comments[index];
						var $html = $(generate_comment(comment)).appendTo($temp);
						bind_events_for_comment($html, comment.id, comment.user_name);
					}
					$temp.children().unwrap().hide().appendTo($commentlist).slideDown(1000);
				}
				loading = false;
			},
			'timeout': 10000
		});
		_gaq.push(['_trackEvent', 'Comment', 'Load', article_id]);
	}

	get_comment();

	//$.getJSON(home_path + 'relative/' + article_id, function(json) {
	//	var length = json ? json.length : 0;
	//	if (length) {
	//		var html = '<ul>';
	//		for (var index = 0; index < length; ++index) {
	//			var article = json[index];
	//			html += '<li><a href="';
	//			html += home_path;
	//			html += article.url;
	//			html += '">';
	//			html += article.title;
	//			html += '</a></li>';
	//		}
	//		html += '</ul>';
	//		$('#relative-articles').append(html).slideDown(1000, function(){
	//			$(this).find('li').animate({'padding-left': '2em'}, 1000);
	//		});
	//	}
	//});
	//_gaq.push(['_trackEvent', 'RelativeArticles', 'Load', article_id]);

	function reply(comment_id, comment_user) {
		if (!allow_comment) {return;}
		var comment = $comment.val();
		comment += '[url=#comment-id-';
		comment += comment_id;
		comment += ']@';
		comment += comment_user;
		comment += '[/url]: ';
		setTimeout(function(){$comment.focus().val(comment);}, 100);
	}

	hljs.configure({tabReplace: '    '});
	$('pre>code').each(function(i, e) {hljs.highlightBlock(e)});

	if ($comment.length) {
		$comment.markItUp(BbcodeSettings);
		var submitting = false;
		var $bbcode = $commentform.find('#bbcode');
		$commentform.submit(function() {
			if (submitting) return false;
			submitting = true;
			var val = $.trim($comment.val());
			if (!val) {
				msgbbox('拜托，你也写点内容再发表吧');
				submitting = false;
				return false;
			}
			var data = {'comment': val};
			if ($bbcode.attr('checked')) {
				data['bbcode'] = 'on';
			}
			$.ajax({
				'url': $commentform.attr('action'),
				'data': data,
				'dataType': 'json',
				'type': 'POST',
				'error': function(){
					submitting = false;
					msgbbox('抱歉，遇到不明状况，发送失败了');
				},
				'success': function(json){
					if (json.status == 200) {
						var comment = json.comment;
						var $html = $(generate_comment(comment));
						bind_events_for_comment($html, comment.id, comment.user_name);
						$html.hide().appendTo($commentlist).slideDown(1000);
						$comment.val('');
						msgbbox('感谢您的回复，由于缓存原因，其他用户可能要几分钟后才能看到您的评论');
					} else {
						msgbbox(json.content);
					}
					submitting = false;
				},
				'timeout': 10000
			});
			_gaq.push(['_trackEvent', 'Comment', 'Reply', article_id]);
			return false;
		});
	}

	if (allow_comment) {
		$('#comments').find('a').click(function() {$comment.focus();});
	}

	$comment_order_asc.click(function() {
		$comment_order_asc.addClass('selected');
		$comment_order_desc.removeClass('selected');
		if (comment_order) {
			return;
		}
		loading = true;
		$commentlist.empty();
		comment_order = true;
		complete = false;
		page = 1;
		get_comment();
	});

	$comment_order_desc.click(function() {
		$comment_order_desc.addClass('selected');
		$comment_order_asc.removeClass('selected');
		if (!comment_order) {
			return;
		}
		loading = true;
		$commentlist.empty();
		comment_order = false;
		complete = false;
		page = 1;
		get_comment();
	});


	if (is_admin) {
		$del_comment_button.click(function() {
			var $parent = $del_comment_button.parent();
			var $comment_li = $parent.parent().parent().parent();
			$.ajax({
				'url': comment_delete_url + $parent.data('id') + '/',
				'dataType': 'json',
				'type': 'POST',
				'error': function(){
					msgbbox('遇到不明状况，评论删除失败了');
				},
				'success': function(json){
					if (json.status == 204) {
						$comment_li.slideUp('2000', function(){
							$del_comment_button.detach();
							$comment_li.remove();
						});
					} else {
						msgbbox(json.content);
					}
				},
				'timeout': 10000
			});
		});
	}

	$more_hint.find('a').click(function () {
		complete = true;
		$more_hint.hide();
	});

	$window.scroll(function(e){
		var currentScrollTop = $window.scrollTop();
		if (!complete && !loading && !_scrolling_status && currentScrollTop > lastScrollTop && ($window.scrollTop() + $window.height() - $respond.offset().top - $respond.outerHeight() > 20)) {
			loading = true;
			get_comment();
		}
		lastScrollTop = currentScrollTop;
		if (_scrolling_status == 2) {_scrolling_status = 0;}
	});
});