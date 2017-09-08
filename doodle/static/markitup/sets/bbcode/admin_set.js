BbcodeSettings = {
	nameSpace: "bbcode",
	previewParserPath:	'/preview/', // path to your BBCode parser
	onTab: {keepDefault:false, replaceWith:'\t'},
	markupSet: [
		{name:'粗体', openWith:'[b]', closeWith:'[/b]'},
		{name:'斜体', openWith:'[i]', closeWith:'[/i]'},
		{name:'下划线', openWith:'[u]', closeWith:'[/u]'},
		{name:'删除线', openWith:'[del]', closeWith:'[/del]'},
		{name:'插入', openWith:'[ins]', closeWith:'[/ins]'},
		{name:'下标', openWith:'[sub]', closeWith:'[/sub]'},
		{name:'上标', openWith:'[sup]', closeWith:'[/sup]'},
		{separator:'---------------' },
		{name:'超链接', openWith:'[url=[![超链接]!]]', closeWith:'[/url]'},
		{name:'图像', replaceWith:'[img][![图像地址]!][/img]'},
		{name:'Flash', replaceWith:'[flash][![Flash地址]!][/flash]'},
		{name:'文字大小', openWith:'[size=[![文字大小]!]]', closeWith:'[/size]',
			dropMenu :[
				{name:'64', openWith:'[size=64]', closeWith:'[/size]' },
				{name:'48', openWith:'[size=48]', closeWith:'[/size]' },
				{name:'32', openWith:'[size=32]', closeWith:'[/size]' },
				{name:'24', openWith:'[size=24]', closeWith:'[/size]' },
				{name:'12', openWith:'[size=12]', closeWith:'[/size]' }
			]
		},
		{	name:'颜色',
			className:'colors',
			openWith:'[color=[![颜色]!]]',
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
		{	name:'背景颜色',
			className:'colors',
			openWith:'[bcolor=[![背景颜色]!]]',
			closeWith:'[/bcolor]',
				dropMenu: [
					{name:'Yellow',	openWith:'[bcolor=yellow]', 	closeWith:'[/bcolor]', className:"col1-1" },
					{name:'Orange',	openWith:'[bcolor=orange]', 	closeWith:'[/bcolor]', className:"col1-2" },
					{name:'Red', 	openWith:'[bcolor=red]', 	closeWith:'[/bcolor]', className:"col1-3" },

					{name:'Blue', 	openWith:'[bcolor=blue]', 	closeWith:'[/bcolor]', className:"col2-1" },
					{name:'Purple', openWith:'[bcolor=purple]', 	closeWith:'[/bcolor]', className:"col2-2" },
					{name:'Green', 	openWith:'[bcolor=green]', 	closeWith:'[/bcolor]', className:"col2-3" },

					{name:'White', 	openWith:'[bcolor=white]', 	closeWith:'[/bcolor]', className:"col3-1" },
					{name:'Gray', 	openWith:'[bcolor=gray]', 	closeWith:'[/bcolor]', className:"col3-2" },
					{name:'Black',	openWith:'[bcolor=black]', 	closeWith:'[/bcolor]', className:"col3-3" }
				]
		},
		{separator:'---------------' },
		{name:'左对齐', openWith:'[align=left]', closeWith:'[/align]'},
		{name:'居中对齐', openWith:'[center]', closeWith:'[/center]'},
		{name:'右对齐', openWith:'[align=right]', closeWith:'[/align]'},
		{name:'无序列表', openWith:'[list]\n[*]', closeWith:'\n[/list]'},
		{name:'有序列表', openWith:'[list=1]\n[*]', closeWith:'\n[/list]'},
		{name:'列表项', openWith:'[*]'},
		{separator:'---------------' },
		{name:'引用', openWith:'[quote]', closeWith:'[/quote]'},
		{name:'代码', openWith:'[code]', closeWith:'[/code]'},
		{name:'短代码', openWith:'[c]', closeWith:'[/c]'},
		{name:'分隔摘要和正文1', openWith:'\n\n[cut1]\n'},
		{name:'分隔摘要和正文2', openWith:'\n\n[cut2]\n'},
		{name:'清除样式', className:"clean", replaceWith:function(markitup) { return markitup.selection.replace(/\[(.*?)\]/g, "") } },
		{name:'预览', className:"preview", call:'preview' }
	]
};