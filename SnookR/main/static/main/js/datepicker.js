// Copyright &copy; 2017 Evan Smelser
// This software is Licensed under the MIT license. For more info please see SnookR/COPYING

$(document).ready(
  function() {
    $( "#id_day" ).datepicker()
    $( "#id_day" ).on("change", function() {
        $( "#id_day" ).datepicker( "option", "dateFormat", "yy-mm-dd" );
    }
    )
});
