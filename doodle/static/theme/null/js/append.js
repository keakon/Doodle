(function(){
	if (ga_id) {
		(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
		(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
		m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
		})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
		ga('create', ga_id, 'auto');
		ga('send', 'pageview');
	}
	var session_time = document.cookie.match(/(^|; ?)session_time=([^;]*)(;|$)/);
	var url = '/page-append?page=' + page;
	if (session_time) {
		url += '&time=' + session_time[2];
	}
	$.ajaxPrefilter('script', function(options) {
		options.cache = true;
	});
	$.ajax({
		'url': url,
		'dataType': 'json',
		'success': function(json) {
			if (json.user_id) {
				var append_links = '<li><a href="' + json.logout_url + '">登出</a></li>';
				if (json.is_admin) {
					append_links += '<li><a href="' + json.admin_url + '">管理博客</a></li>';
				}
				if (ga_id) {
					ga('set', 'userId', json.user_id);
				}
			} else {
				append_links = '<li><a href="' + json.login_url + '">登录</a></li>';
			}
			$('#nav').append(append_links);
			if (json.append_js_urls) {
				var js_urls = json.append_js_urls;
				var scripts = [];
				for (var i = 0; i < js_urls.length; ++i) {
					scripts.push('<script src="' + js_urls[i] + '"></script>')
				}
				$('head').append(scripts.join(''));
			}
			if (page == 'article') {
				show_comment_form(json.user_name, json.comment_url_prefix ? json.comment_url_prefix + article_id : '', json.logout_url, json.profile_url, json.login_url);
				if (json.is_admin) {
					$('.post-data').append('<span id="post-operation"><a href="' + json.edit_url_prefix + article_id + '/edit">[编辑]</a></span>');
				}
			}
		},
		'timeout': 10000
	});
})();