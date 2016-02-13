$(function(){
	var submitting = false;
	var $info = $('.msg');
	function show(text){
		$info.html(text);
		submitting = false;
	}
	$('#del-token').click(function(){
		if (!submitting) {
			submitting = true;
			$.ajax({
				'type': 'POST',
				'error': function(){
					show('抱歉，遇到不明状况，发送失败了');
				},
				'success': show,
				'timeout': 10000
			});
		}
	});
});