(function(){
var colors = ['#8431cf', '#1332df', '#f00122', '#8c4211', '#de3f90', '#666', '#05d30d', '#e957ea', '#007aad', '#f00'];
var length = colors.length;
$('#tags a').each(function(){
	$(this).css('color', colors[Math.floor(Math.random() * length)]);
});
})();