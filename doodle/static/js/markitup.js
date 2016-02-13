$(function(){
	var $textarea = $('#content').markItUp(BbcodeSettings);
	$('.switcher li').click(function() {
		$textarea.markItUpRemove();
		switch (this.className) {
			case 'bbcode':
				$textarea.markItUp(BbcodeSettings);
				break;
			case 'html':
				$textarea.markItUp(HtmlSettings);
		}
		return false;
	});
});