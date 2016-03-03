var _scrolling_status = 0; // 0: stopped; 1: scrolling; 2: stopping
(function(){
	var $scroller;
	var $body = $('body');
	var $html = $('html');
	if ($body.scrollTop()) {
		$scroller = $body;
	} else if ($html.scrollTop()) {
		$scroller = $html;
	} else {
		$body.scrollTop(1);
		if ($body.scrollTop()) {
			$scroller = $body.scrollTop(0);
		} else {
			$scroller = $html;
		}
	}
	function scrollTo(top) {
		_scrolling_status = 1;
		$scroller.animate({scrollTop: top < 0 ? 0 : top}, 1000, function() {_scrolling_status = 2;});
	}
	$body.on('click', 'a[href^=#]', function(ev) {
		var hash = this.hash;
		if (hash) {
			var $hash = $(hash);
			if ($hash.length) {
				scrollTo($hash.offset().top);
				ev.preventDefault();
			}
		} else {
			scrollTo(0);
			ev.preventDefault();
		}
	});
	$.fn.extend({
		'scrollTo': function() {
			scrollTo(this.offset().top);
			return this;
		}
	});
})();