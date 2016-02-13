$(function(){
	var submitting = false;
	var $info = $('.info');
	var $body = $('body');
	var $html = $('html');
	var timeout;
	function show(text){
		$info.html(text).addClass('new-info').show();
		if (timeout) {
			clearTimeout(timeout);
		}
		timeout = setTimeout(function() {
			$info.removeClass('new-info');
		}, 3000);
		submitting = false;
		if ($body.scrollTop()) {
			$body.animate({scrollTop: 0}, 500);
		} else if ($html.scrollTop()) {
			$html.animate({scrollTop: 0}, 500);
		}
	}
	function ajax_get(url){
		$.ajax({
			'url': url,
			'type': 'GET',
			'error': function(){
				show('抱歉，遇到不明状况，发送失败了');
			},
			'success': show,
			'timeout': 10000
		});
	}
	$('#flush-cache').click(function(){
		if (!submitting) {
			submitting = true;
			ajax_get('/admin/flush_cache');
		}
	});
	$('#generate-sitemap').click(function(){
		if (!submitting) {
			submitting = true;
			ajax_get('/admin/generate_sitemap?id=1');
		}
	});
	$('#generate-missing-entities').click(function(){
		if (!submitting) {
			submitting = true;
			ajax_get('/admin/generate_missing_entities');
		}
	});
	$('#generate-feed').click(function(){
		if (!submitting) {
			submitting = true;
			ajax_get('/admin/generate_feed');
		}
	});
	$('#update-tags-count').click(function(){
		if (!submitting) {
			submitting = true;
			ajax_get('/admin/update_tags_count');
		}
	});
	$('#update-articles-replies').click(function(){
		if (!submitting) {
			submitting = true;
			ajax_get('/admin/update_articles_replies');
		}
	});
	$('#remove-old-subscribers').click(function(){
		if (!submitting) {
			submitting = true;
			ajax_get('/admin/remove_old_subscribers');
		}
	});
});