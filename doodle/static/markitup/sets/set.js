BbcodeSettings = {
	nameSpace: "bbcode",
	previewParserPath:	'/preview/', // path to your BBCode parser
	markupSet: [
		{name:'Bold', key:'B', openWith:'[b]', closeWith:'[/b]'},
		{name:'Italic', key:'I', openWith:'[i]', closeWith:'[/i]'},
		{name:'Underline', key:'U', openWith:'[u]', closeWith:'[/u]'},
		{name:'Stroke', key:'D', openWith:'[del]', closeWith:'[/del]'},
		{name:'Sub', openWith:'[sub]', closeWith:'[/sub]'},
		{name:'Sup', openWith:'[sup]', closeWith:'[/sup]'},
		{separator:'---------------' },
		{name:'Link', key:'L', openWith:'[url=[![Url]!]]', closeWith:'[/url]', placeHolder:'Your text to link here...'},
		{name:'Picture', key:'P', replaceWith:'[img][![Url]!][/img]'},
		{name:'Flash', replaceWith:'[flash][![Url]!][/flash]'},
		{name:'Size', openWith:'[size=[![Text size]!]]', closeWith:'[/size]',
			dropMenu :[
				{name:'64', openWith:'[size=64]', closeWith:'[/size]' },
				{name:'48', openWith:'[size=48]', closeWith:'[/size]' },
				{name:'32', openWith:'[size=32]', closeWith:'[/size]' },
				{name:'24', openWith:'[size=24]', closeWith:'[/size]' },
				{name:'12', openWith:'[size=12]', closeWith:'[/size]' }
			]
		},
		{	name:'Colors',
			className:'colors',
			openWith:'[color=[![Color]!]]',
			closeWith:'[/color]',
				dropMenu: [
					{name:'Yellow',	openWith:'[color=yellow]', 	closeWith:'[/color]', className:"col1-1" },
					{name:'Orange',	openWith:'[color=orange]', 	closeWith:'[/color]', className:"col1-2" },
					{name:'Red', 	openWith:'[color=red]', 	closeWith:'[/color]', className:"col1-3" },

					{name:'Blue', 	openWith:'[color=blue]', 	closeWith:'[/color]', className:"col2-1" },
					{name:'Purple', openWith:'[color=purple]', 	closeWith:'[/color]', className:"col2-2" },
					{name:'Green', 	openWith:'[color=green]', 	closeWith:'[/color]', className:"col2-3" },

					{name:'White', 	openWith:'[color=white]', 	closeWith:'[/color]', className:"col3-1" },
					{name:'Gray', 	openWith:'[color=gray]', 	closeWith:'[/color]', className:"col3-2" },
					{name:'Black',	openWith:'[color=black]', 	closeWith:'[/color]', className:"col3-3" }
				]
		},
		{separator:'---------------' },
		{name:'Left', openWith:'[align=left]', closeWith:'[/align]'},
		{name:'Center', openWith:'[center]', closeWith:'[/center]'},
		{name:'Right', openWith:'[align=right]', closeWith:'[/align]'},
		{name:'Bulleted list', openWith:'[list]\n[*]', closeWith:'\n[/list]'},
		{name:'Numeric list', openWith:'[list=[![Starting number]!]]\n[*]', closeWith:'\n[/list]'},
		{name:'List item', openWith:'[*]'},
		{separator:'---------------' },
		{name:'Quotes', openWith:'[quote]', closeWith:'[/quote]'},
		{name:'Code', openWith:'[code]', closeWith:'[/code]'},
		{name:'Clean', className:"clean", replaceWith:function(markitup) { return markitup.selection.replace(/\[(.*?)\]/g, "") } },
		{name:'Preview', className:"preview", call:'preview' }
	]
};

myHtmlSettings = {
	nameSpace: "html",
	onShiftEnter:	{keepDefault:false, replaceWith:'<br />\n'},
	onCtrlEnter:	{keepDefault:false, openWith:'\n<p>', closeWith:'</p>\n'},
	onTab:			{keepDefault:false, openWith:'	 '},
	markupSet: [
		{name:'Heading 1', key:'1', openWith:'<h1(!( class="[![Class]!]")!)>', closeWith:'</h1>', placeHolder:'Your title here...' },
		{name:'Heading 2', key:'2', openWith:'<h2(!( class="[![Class]!]")!)>', closeWith:'</h2>', placeHolder:'Your title here...' },
		{name:'Heading 3', key:'3', openWith:'<h3(!( class="[![Class]!]")!)>', closeWith:'</h3>', placeHolder:'Your title here...' },
		{name:'Heading 4', key:'4', openWith:'<h4(!( class="[![Class]!]")!)>', closeWith:'</h4>', placeHolder:'Your title here...' },
		{name:'Heading 5', key:'5', openWith:'<h5(!( class="[![Class]!]")!)>', closeWith:'</h5>', placeHolder:'Your title here...' },
		{name:'Heading 6', key:'6', openWith:'<h6(!( class="[![Class]!]")!)>', closeWith:'</h6>', placeHolder:'Your title here...' },
		{name:'Paragraph', openWith:'<p(!( class="[![Class]!]")!)>', closeWith:'</p>' },
		{separator:'---------------' },
		{name:'Bold', key:'B', openWith:'(!(<strong>|!|<b>)!)', closeWith:'(!(</strong>|!|</b>)!)' },
		{name:'Italic', key:'I', openWith:'(!(<em>|!|<i>)!)', closeWith:'(!(</em>|!|</i>)!)' },
		{name:'Stroke through', key:'S', openWith:'<del>', closeWith:'</del>' },
		{name:'Colors', className:'palette', dropMenu: [
				{name:'Yellow',	replaceWith:'#FCE94F',	className:"col1-1" },
				{name:'Yellow',	replaceWith:'#EDD400', 	className:"col1-2" },
				{name:'Yellow', replaceWith:'#C4A000', 	className:"col1-3" },

				{name:'Orange', replaceWith:'#FCAF3E', 	className:"col2-1" },
				{name:'Orange', replaceWith:'#F57900', 	className:"col2-2" },
				{name:'Orange', replaceWith:'#CE5C00', 	className:"col2-3" },

				{name:'Brown', 	replaceWith:'#E9B96E', 	className:"col3-1" },
				{name:'Brown', 	replaceWith:'#C17D11', 	className:"col3-2" },
				{name:'Brown',	replaceWith:'#8F5902', 	className:"col3-3" },

				{name:'Green', 	replaceWith:'#8AE234', 	className:"col4-1" },
				{name:'Green', 	replaceWith:'#73D216', 	className:"col4-2" },
				{name:'Green',	replaceWith:'#4E9A06', 	className:"col4-3" },

				{name:'Blue', 	replaceWith:'#729FCF', 	className:"col5-1" },
				{name:'Blue', 	replaceWith:'#3465A4', 	className:"col5-2" },
				{name:'Blue',	replaceWith:'#204A87', 	className:"col5-3" },

				{name:'Purple', replaceWith:'#AD7FA8', 	className:"col6-1" },
				{name:'Purple', replaceWith:'#75507B', 	className:"col6-2" },
				{name:'Purple',	replaceWith:'#5C3566', 	className:"col6-3" },

				{name:'Red', 	replaceWith:'#EF2929', 	className:"col7-1" },
				{name:'Red', 	replaceWith:'#C00', 	className:"col7-2" },
				{name:'Red',	replaceWith:'#A40000', 	className:"col7-3" },

				{name:'Gray', 	replaceWith:'#FFF', 	className:"col8-1" },
				{name:'Gray', 	replaceWith:'#D3D7CF', 	className:"col8-2" },
				{name:'Gray',	replaceWith:'#BABDB6', 	className:"col8-3" },

				{name:'Gray', 	replaceWith:'#888A85', 	className:"col9-1" },
				{name:'Gray', 	replaceWith:'#555753', 	className:"col9-2" },
				{name:'Gray',	replaceWith:'#000', 	className:"col9-3" }
			]
		},
		{separator:'---------------' },
		{name:'Ul', openWith:'<ul>\n', closeWith:'</ul>\n' },
		{name:'Ol', openWith:'<ol>\n', closeWith:'</ol>\n' },
		{name:'Li', openWith:'<li>', closeWith:'</li>' },
		{separator:'---------------' },
		{name:'Picture', key:'P', replaceWith:'<img src="[![Source:!:http://]!]" alt="[![Alternative text]!]" />' },
		{name:'Link', key:'L', openWith:'<a href="[![Link:!:http://]!]"(!( title="[![Title]!]")!)>', closeWith:'</a>', placeHolder:'Your text to link...' },
		{separator:'---------------' },
		{name:'Clean', className:'clean', replaceWith:function(markitup) { return markitup.selection.replace(/<(.*?)>/g, "") } },
		{name:'Preview', className:'preview', call:'preview' }
	]
};