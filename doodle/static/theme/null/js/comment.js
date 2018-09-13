$(function() {
	var $window = $(window);
	var complete = false;
	var loading = true;
	var lastScrollTop = 0;
	var $commentlist = $('#commentlist>ol');
	var $temp = $('<ol/>');
	var $comment_float_list = $('<ol class="commentlist comment-float-list"/>').appendTo(document.body).hide();
	var $comment, $commentform, allow_comment;
	var page = 1;
	var comment_order = true;
	var $comment_order_asc = $('#comment-order-asc');
	var $comment_order_desc = $('#comment-order-desc');
	var comment_fetch_url = home_path + 'article/'+ article_id + '/comments/';
	var is_admin = typeof(ban_url) != 'undefined';
	var $ban_button = $('<span id="ban-button" class="comment-action-button">确认禁言</span>');
	var $del_comment_button = $('<span id="del-comment-button" class="comment-action-button">确认删除</span>');
	var $del_user_comments_button = $('<span id="del-user-comments-button" class="comment-action-button">确认删除</span>');
	var $more_hint = $('#more-hint');
	var $respond = $('#respond');
	var url_hash = location.hash;
	var now = new Date();

	var escape_map = {
		'&': '&amp;',
		'<': '&lt;',
		'>': '&gt;',
		'"': '&quot;',
		"'": '&#x27;'
	};
	function replacer(char) {
		return escape_map[char];
	}
	function escape_html(string) {
		return string.replace(/[&<>"']/g, replacer);
	}

	function generate_comment(comment) {
		var html = '<li><p class="comment-author"><img src="';
		html += comment.img;
		html += '?s=48&amp;d=monsterid" class="avatar" height="48" width="48"/><cite><a id="comment-id-';
		html += comment.id;
		if (comment.url) {
			html += '" href="' + escape_html(comment.url);
		}
		html += '">' + escape_html(comment.user_name) + '</a></cite>';
		var uas = comment.ua;
		if (uas) {
			html += '<span class="ua">';
			for (var i = 0, ua; i < uas.length; ++ i) {
				ua = comment.ua[i];
				html += '<img src="/static/img/ua/' + ua.replace(/ /g, '-') + '.png" alt="' + ua + '" title="' + ua + '"/>';
			}
			html += '</span>';
		}
		html += '<br/><small><strong>' + comment.time + '</strong>';
		if (is_admin) {
			html += ' <span class="ban-user comment-action">[禁言]</span> <span class="del-comment comment-action">[删除]</span> <span class="del-user-comments comment-action">[全部删除]</span>'
		}
		html += '</small></p><div class="commententry" id="commententry-' + comment.id + '"><div>' + comment.content + '</div></div><a class="comment-reply-link" href="#respond">回复</a></li>';
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
			$html.find('span.ban-user').data('id', id).hover(function(){
				$(this).append($ban_button);
			}, function(){
				$ban_button.detach();
			});
			$html.find('span.del-comment').data('id', id).hover(function(){
				$(this).append($del_comment_button);
			}, function(){
				$del_comment_button.detach();
			});
			$html.find('span.del-user-comments').data('id', id).hover(function(){
				$(this).append($del_user_comments_button);
			}, function(){
				$del_user_comments_button.detach();
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
					if (url_hash) {
						if (new Date() - now < 5000) { // 载入 5 秒内，自动定位
							if (!scroller.is_scrolling()) {
								$(url_hash).scrollTo();
							}
						}
						url_hash = null; // prevent scroll twice
					}
				}
				loading = false;
				ga_id && ga('send', 'event', 'Comment', 'Load', null, article_id);
			},
			'timeout': 10000
		});
	}

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

	$.extend({
		'show_comment_form': function(user_name, action_url, logout_url, profile_url, login_url) {
			if (login_url) {
				$respond.append('<p>您需要<a href="' + login_url + '">登录</a>您的 Google 账号才能进行评论。</p>');
			} else {
				$respond.append(
'<form action="' + action_url + '" method="post" id="commentform">\
	<p>您当前登录的用户为：' + escape_html(user_name) + '，您可<a href="' + profile_url + '">修改用户资料</a>，或<a href="' + logout_url + '">登出</a>以更换用户。</p>\
	<p><textarea name="comment" id="comment" cols="58" rows="10" tabindex="1"></textarea></p>\
	<p><input name="bbcode" type="checkbox" id="bbcode" tabindex="2" checked="checked"/> <label for="bbcode">启用BBCode</label></p>\
	<p><small>小提示：回复某条回帖时，可以点击其右侧的“回复”按钮，这样该帖的作者会收到邮件通知。</small></p>\
	<p><input name="submit" type="submit" id="submit" tabindex="3" value="来一发"/></p>\
</form>');

				allow_comment = true;
				$comment = $('#comment');
				$commentform = $('#commentform');
				$comment.markItUp(BbcodeSettings);
				$('#comments').find('a').click(function() {$comment.focus();});

				var submitting = false;
				var $bbcode = $commentform.find('#bbcode');
				$commentform.submit(function() {
					if (submitting) return false;
					submitting = true;
					var val = $.trim($comment.val());
					if (!val) {
						$.msgbox('拜托，你也写点内容再发表吧');
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
						'error': function(xhr) {
							submitting = false;
							$.msgbox(xhr.status == 403 ? '抱歉，您需要登录才能发表评论' : '抱歉，遇到不明状况，发送失败了');
						},
						'success': function(json) {
							var comment = json.comment;
							var $html = $(generate_comment(comment));
							bind_events_for_comment($html, comment.id, comment.user_name);
							$html.hide().appendTo($commentlist).slideDown(1000);
							$comment.val('');
							$.msgbox('评论成功');
							submitting = false;
							ga_id && ga('send', 'event', 'Comment', 'Reply', null, article_id);
						},
						'timeout': 10000
					});
					return false;
				});
			}
		}
	});

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

	if (url_hash) {
		$comment_order_desc.click();
	} else {
		get_comment();
	}

	$more_hint.find('a').click(function () {
		complete = true;
		$more_hint.hide();
	});

	if (is_admin) {
		$ban_button.click(function() {
			var $parent = $ban_button.parent();
			var $comment_li = $parent.parent().parent().parent();
			$.ajax({
				'url': ban_url + $parent.data('id'),
				'dataType': 'json',
				'type': 'POST',
				'error': function(){
					msgbbox('遇到不明状况，禁言失败了');
				},
				'success': function(json){
					$ban_button.detach();
				},
				'timeout': 10000
			});
		});

		$del_comment_button.click(function() {
			var $parent = $del_comment_button.parent();
			var $comment_li = $parent.parent().parent().parent();
			$.ajax({
				'url': delete_comment_url + $parent.data('id'),
				'dataType': 'json',
				'type': 'DELETE',
				'error': function(){
					msgbbox('遇到不明状况，评论删除失败了');
				},
				'success': function(json){
					$comment_li.slideUp('2000', function(){
						$del_comment_button.detach();
						$comment_li.remove();
					});
				},
				'timeout': 10000
			});
		});

		$del_user_comments_button.click(function() {
			var $parent = $del_user_comments_button.parent();
			var $comment_li = $parent.parent().parent().parent();
			$.ajax({
				'url': delete_user_comments_url + $parent.data('id'),
				'dataType': 'json',
				'type': 'DELETE',
				'error': function(){
					msgbbox('遇到不明状况，评论删除失败了');
				},
				'success': function(json){
					$comment_li.slideUp('2000', function(){
						$del_comment_button.detach();
						$comment_li.remove();
					});
				},
				'timeout': 10000
			});
		});
	}

	$window.scroll(function(e){
		var currentScrollTop = $window.scrollTop();
		if (!complete && !loading && !scroller.is_scrolling() && currentScrollTop > lastScrollTop && ($window.scrollTop() + $window.height() - $respond.offset().top - $respond.outerHeight() > 20)) {
			loading = true;
			get_comment();
		}
		lastScrollTop = currentScrollTop;
		if (scroller.is_stopping()) {scroller.set_stopped();}
	});
});