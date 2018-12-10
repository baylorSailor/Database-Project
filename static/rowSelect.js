

alert('hi');

$("#queryTable tr").click(function(){
   alert('');
});

$('.ok').on('click', function(e){
    alert($("#table tr.selected td:first").html());
});