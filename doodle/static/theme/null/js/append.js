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
	$.ajax({
		'url': url,
		'dataType': 'json',
		'success': function(data) {
			if (data.user_id) {
				var append_links = '<li><a href="' + data.logout_url + '">登出</a></li>';
				if (data.is_admin) {
					append_links += '<li><a href="' + data.admin_url + '">管理博客</a></li>';
				}
				if (ga_id) {
					ga('set', 'userId', data.user_id);
				}
			} else {
				append_links = '<li><a href="' + data.login_url + '">登录</a></li>';
			}
			$('#nav').append(append_links);
			if (data.append_js_urls) {
				// 用 jQuery 的话会变成 ajax 请求，并且 HTTP/2 的请求会降级成 HTTP/1.x
				var js_urls = data.append_js_urls;
				var js_count = js_urls.length;
				var loaded_js = 0;
				var on_js_load = function() {
					loaded_js += 1;
					if (loaded_js == js_count) {
						if (page == 'article') {
							$.show_comment_form(data.user_name, data.comment_url_prefix ? data.comment_url_prefix + article_id : '', data.logout_url, data.profile_url, data.login_url);
						}
					}
					this.onload = this.onreadystatechange = null;
				};
				var on_js_ready_state_change = function() {
					if (this.readyState === "complete") {
						on_js_load();
					}
				};
				for (var i = 0; i < js_count; ++i) {
					var script = document.createElement('script');
					script.async = 1;
					script.src = js_urls[i];
					script.onload = on_js_load;
					script.onreadystatechange = on_js_ready_state_change;
					document.body.appendChild(script);
				}
			} else {
				$.show_comment_form('', '', '', '', data.login_url);
			}
			if (page == 'article') {
				if (data.is_admin) {
					$('.post-data').append('<span id="post-operation"><a href="' + data.edit_url_prefix + article_id + '/edit">[编辑]</a></span>');
				}
			}
		},
		'timeout': 10000
	});
})();