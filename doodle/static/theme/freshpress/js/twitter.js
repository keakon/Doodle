$(function(){
	var $content = $('#content');
	var $count = $('#left-count');
	var pattern = /(?:^|(?:[^0-9a-zA-Z_\-!@='"\/\.]))((?:https?:\/\/)?(?:[^/?#\x00-\x20\x7f-\uffff]*@[^/?#\x00-\x20\x7f-\uffff]*:)?[0-9a-zA-Z][0-9a-zA-Z\-\.]*\.[a-zA-Z]{2,4}(?::(?:[0-9]){1,5})?(?:\/(?:[^\x00-\x20\x7f-\uffff]*)?))/g;
	var timer = 0;
	$content.focus(function() {
		if (!timer) {
			timer = setInterval(function() {
				var content = $content.val();
				var length = content.length;
				if (length > 10) {
					var url;
					while (url = pattern.exec(content)) {
						length += 20 - url[1].length;
					}
				}
				var left = 140 - length;
				$count.text(left);
				if (left < 0) {
					$count.addClass('neg');
				} else {
					$count.removeClass('neg');
				}
			}, 200);
		}
	}).blur(function() {
		clearInterval(timer);
		timer = 0;
	});
});