$(function() {
	var $window = $(window);
	var $content = $('#content');
	var top = $content.offset().top;
	var $loading = $('<div/>');
	var loading = false;
	var $next_url = $('#content>.post-nav>.previous>a');
	var next_url = '';
	var $no_more = $('<span class="no-more"><a href="javascript:;">停止自动加载</a></span>');

	$no_more.find('a').click(function() {
		$window.off('scroll', load_more);
		$no_more.remove();
	});

	function set_next_url() {
		if ($next_url.length) {
			next_url = $next_url.attr('href');
		} else {
			$window.off('scroll', load_more);
			next_url = '';
		}
	}

	function load() {
		$loading.load(next_url + ' #content', function() {
			$next_url = $loading.find('.post-nav>.previous>a');
			set_next_url();
			$next_url.parent().after($no_more);
			$('#content>.post-nav').detach();
			$loading.children().detach().children().hide().appendTo($content).slideDown(1000);
			loading = false;
		});
		_gaq.push(['_trackEvent', 'Page', 'Load', next_url]);
	}

	function load_more() {
		if (!loading && ($window.scrollTop() + $window.height() - top - $content.outerHeight() > 80)) {
			loading = true;
			load();
		}
	}

	$window.on('scroll', load_more);
	set_next_url();
});