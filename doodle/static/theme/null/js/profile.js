(function(){
	var submitting = false;
	var $form = $('#profileform');
	$form.submit(function() {
		if (submitting) return false;
		submitting = true;
		$.ajax({
			'data': $form.serialize(),
			'type': 'POST',
			'error': function(){
				submitting = false;
				msgbbox('抱歉，遇到不明状况，保存失败了');
			},
			'success': function(text){
				msgbbox(text);
				submitting = false;
			},
			'timeout': 10000
		});
		return false;
	});
})();