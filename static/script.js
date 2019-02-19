$(document).ready(function() {
    $('select').material_select();
    $('input#disc1_rate, input#disc2_rate, input#disc3_rate, input#vp_time').characterCounter();
    
    
    let chartVals= {};
    chartVals.Names = []; chartVals.BR = []; chartVals.VR = [];
    $('.player').each(function(i, obj) {
        console.log(i,obj); /* $(this) */
        chartVals.Names.push($(this).find("td:eq(1)").text()); //name
        chartVals.BR.push($(this).find("td:eq(3)").text()); //birth_region
        chartVals.VR.push($(this).find("td:eq(8)").text()); //virtual_rate
    });
    
    console.log(chartVals);
    console.log(chartVals["Names"]);
    console.log(chartVals["BR"]);
    console.log(chartVals["VR"]);
});
