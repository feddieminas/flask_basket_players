$(document).ready(function() {
    $('select').material_select();
    $('input#disc1_rate, input#disc2_rate, input#disc3_rate, input#vp_time').characterCounter();
    $('#modal_edit').modal(); $('#modal_dele').modal();
    
    /*
    $('#modal_edit').modal({
          dismissible: true, // Modal can be dismissed by clicking outside of the modal
          opacity: .5, // Opacity of modal background
          inDuration: 300, // Transition in duration
          outDuration: 200, // Transition out duration
          startingTop: '4%', // Starting top style attribute
          endingTop: '10%', // Ending top style attribute
          ready: function(modal, trigger) { // Callback for Modal open, once it opens. Modal and trigger parameters available.
            alert("Ready");
            console.log(modal, trigger);
          },
          complete: function() { alert('Closed'); } // Callback for Modal close, once it closes
        }
      );
    */    
    
    let chartVals= {};
    chartVals.Names = []; chartVals.BR = []; chartVals.VR = [];
    $('.player').each(function(i, obj) {
        //console.log(i,obj); /* $(this) */
        chartVals.Names.push($(this).find("td:eq(1)").text()); //name
        chartVals.BR.push($(this).find("td:eq(3)").text()); //birth_region
        chartVals.VR.push($(this).find("td:eq(8)").text()); //virtual_rate
    });
    
    /*
    console.log(chartVals);
    console.log(chartVals["Names"]);
    console.log(chartVals["BR"]);
    console.log(chartVals["VR"]);
    */
    
});
