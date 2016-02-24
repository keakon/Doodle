$(function() {
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

	if (typeof article_id === 'number') {
		var is_article_page = true;
		// 保存文章后，会带上时间参数以避免拿到缓存的内容
		// 这里会去掉这些参数，使 URL 比较好看，但可能影响 GA 的统计
		history.replaceState(null, '', location.pathname);
	} else {
		is_article_page = false;
	}

	if (!localStorage.session_time || parseInt(localStorage.session_time).isNaN()) {
		localStorage.clear();
	}
	var fetch = !localStorage.session_time;
	var url = '/page-append';
	var match = document.cookie.match(/(^|; ?)session_time=([^;]*)(;|$)/);
	if (match) {
		var session_time = match[2];
		if (localStorage.session_time < session_time) { // a new session started, should reload config
			localStorage.clear();
			url += '?t=' + session_time;
			fetch = true;
		}
	}
	if (fetch) {
		fetch_config().then(save_config).then(modify_page);
	} else {
		modify_page();
	}

	function fetch_config() {
		return $.ajax({
			'url': url,
			'dataType': 'json',
			'timeout': 10000
		});
	}

	function save_config(config) {
		localStorage.session_time = session_time || 0;
		for (var key in config) {
			var value = config[key];
			if (typeof value != 'string') {
				value = JSON.stringify(value);
			}
			localStorage[key] = value;
		}
	}

	function modify_page() {
		var config = localStorage;
		if (config.has_logged_in) {
			var append_links = '<li><a href="' + config.logout_url + '">登出</a></li>';
			if (config.is_admin) {
				append_links += '<li><a href="' + config.admin_url + '">管理博客</a></li>';
			}
		} else {
			append_links = '<li><a href="' + config.login_url + '">登录</a></li>';
		}
		$('#nav').append(append_links);

		if (is_article_page) {
			if (config.is_admin) {
				$('.post-data').append('<span id="post-operation"><a href="' + config.edit_url_prefix + article_id + '/edit">[编辑]</a></span>');
			}
			if (config.article_js_urls) {
				var js_urls = JSON.parse(config.article_js_urls);
				var js_count = js_urls.length;
				if (js_count) {
					var requests = [];
					for (var i = 0; i < js_count; ++i) {
						requests.push($.getScript(js_urls[i]));
					}
					$.when.apply($, requests).done(function() {
						$.show_comment_form(config.user_name, config.comment_url_prefix ? config.comment_url_prefix + article_id : '', config.logout_url, config.profile_url, config.login_url);
					});
				}
			} else {
				$.show_comment_form('', '', '', '', config.login_url);
			}
		}
	}
});