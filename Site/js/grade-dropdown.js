for(var i=4; i<=12; i++){
    var select = document.getElementById("grade");
    var option = document.createElement("OPTION");
	select.options.add(option);
	option.text = i;
	option.value = i;
}