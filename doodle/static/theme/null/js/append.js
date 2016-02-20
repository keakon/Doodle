(function(){
	if (ga_id) {
		(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
		(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
		m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
		})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
		ga('create', ga_id, 'auto');
		ga('send', 'pageview');
	}
	$.ajaxPrefilter('script', function(options) {
		options.cache = true;
	});
	var session_time = document.cookie.match(/(^|; ?)session_time=([^;]*)(;|$)/);
	var url = '/page-append?page=' + page;
	if (session_time) {
		url += '&time=' + session_time[2];
	}
	$.ajax({
		'url': url,
		'dataType': 'json',
		'success': function(data) {
			if (data.user_id) {
				var append_links = '<li><a href="' + data.logout_url + '">登出</a></li>';
				if (data.is_admin) {
					append_links += '<li><a href="' + data.admin_url + '">管理博客</a></li>';
				}
				ga_id && ga('set', 'userId', data.user_id);
			} else {
				append_links = '<li><a href="' + data.login_url + '">登录</a></li>';
			}
			$('#nav').append(append_links);

			if (data.append_js_urls) {
				var js_urls = data.append_js_urls;
				var js_count = js_urls.length;
				var requests = [];
				for (var i = 0; i < js_count; ++i) {
					requests.push($.getScript(js_urls[i]));
				}
				if (page == 'article') {
					$.when.apply($, requests).done(function() {
						$.show_comment_form(data.user_name, data.comment_url_prefix ? data.comment_url_prefix + article_id : '', data.logout_url, data.profile_url, data.login_url);
					});
				}
			}

			if (page == 'article') {
				if (data.is_admin) {
					$('.post-data').append('<span id="post-operation"><a href="' + data.edit_url_prefix + article_id + '/edit">[编辑]</a></span>');
				}
				if (!data.append_js_urls) {
					$.show_comment_form('', '', '', '', data.login_url);
				}
			}
		},
		'timeout': 10000
	});
})();