var scroller = (function() {
	var status = 0; // 0: stopped; 1: scrolling; 2: stopping
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
	var scroller = {
		is_scrolling: function() {
			return status != 0;
		},
		is_stopping: function() {
			return status == 2;
		},
		set_stopped: function() {
			status = 0;
		},
		scrollTo: function(top) {
			status = 1;
			$scroller.animate({scrollTop: top < 0 ? 0 : top}, 1000, function () {
				status = 2;
			});
		}
	};
	$.fn.extend({
		'scrollTo': function() {
			if (this.length) {
				scroller.scrollTo(this.offset().top);
			}
			return this;
		}
	});
	$body.on('click', 'a[href^=#]', function(ev) {
		var hash = this.hash;
		if (hash) {
			var $hash = $(hash);
			if ($hash.length) {
				$hash.scrollTop();
				ev.preventDefault();
			}
		} else {
			scroller.scrollTo(0);
			ev.preventDefault();
		}
	});
	return scroller;
})();