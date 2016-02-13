var $msgbox = $('<div id="msgbox"/>').appendTo(document.body);
var $window = $(window);
function msgbbox(html) {
	$msgbox.html(html).css({
		'left': (($window.width() - $msgbox.width()) / 2 + 'px'),
		'top': (($window.height() - $msgbox.height()) / 2 + $window.scrollTop() + 'px')
	}).fadeIn(2000, function() {
		$msgbox.animate({top: '+=30px'}, {duration: 1000, queue: false}).fadeOut(1000);
	});
}