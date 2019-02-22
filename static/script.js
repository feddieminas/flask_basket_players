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

//});    
    ////////////////////////////////////////////////
    
    function hasNameSurname(s) {return /[,.\s\/]/g.test(s);}
    
    function findSplitSeparator(s) {
        match = /[,.\s\/]/g.exec(s);
        return match[0];
    }
    
    function fitName(nameField) {
        nameField = nameField.replace(/^\s+/,""); //left trim
        nameField = nameField.replace(/\s$/, "");  //right trim
        if (hasNameSurname(nameField)) {
            splitNameSurname=nameField.split(findSplitSeparator(nameField));
            theName = splitNameSurname[0].slice(0,1); //Name
            theSurname = splitNameSurname[splitNameSurname.length-1].slice(0,8); //Surname
            nameField = theName + '. ' + theSurname;
        }    
        else {
            nameField=nameField.slice(0,9);     
        }
        return nameField; 
    }
    
    //in  the end to isert all
    if (!$(".player")[0]){
        //Do something if class not exists"
    } else {
        //"Do something if class exists"
        
        //queue()
            //.defer(d3.json, "temp.json") 
            //.await(makeGraphs); 
        
        //function makeGraphs(error, data) {
            //console.log(data);
        //}

        //let chartVals= {}; 
        //chartVals.Names = []; chartVals.BR = []; chartVals.VR = [];
        let barchartVals= []; 
        let piechartVals= [{"label": "Europe","value": 1}, {"label": "Europe","value": 1}, {"label": "America","value": 1},{"label": "Asia","value": 1}
        ,{"label": "Asia","value": 1},{"label": "Africa","value": 1},{"label": "Africa","value": 1}];
        $('.player').each(function(i, obj) {
            //console.log(i,obj); /* $(this) */
            barchartVals.push({"name": $(this).find("td:eq(1)").text(),"value": parseFloat($(this).find("td:eq(8)").text())});
            //chartVals.Names.push($(this).find("td:eq(1)").text()); //name
            //chartVals.BR.push($(this).find("td:eq(3)").text()); //birth_region
            //chartVals.VR.push($(this).find("td:eq(8)").text()); //virtual_rate
        });
        
        //console.log(barchartVals);
        //console.log(chartVals["Names"]);
        //console.log(chartVals["BR"]);
        //console.log(chartVals["VR"]); 
        //console.log(chartVals["VR"][0])
        
        valsCount = barchartVals.length;
        if (valsCount>5) {valsCount=5};
        
        //console.log(valsCount);
        
        barchartVals = barchartVals.sort(function (a, b) {
                return d3.descending(a.value, b.value);
        }).slice(0,valsCount);
        
        barchartVals.map(function(item) {
            item.name = fitName(item.name);
            //console.log("item", item); 
        });         
        
        //console.log(barchartVals);
        
        const maxVal = barchartVals[valsCount-1]["value"];
        const minVal = barchartVals[0]["value"];
        
        const margin = { // 5,28,20,70
                top: 5,
                right: 28,
                bottom: 0,
                left: 70
            };
    
        //350,250
        const width = 350 - margin.left - margin.right, height = 250 - margin.top - margin.bottom;    
        
        let svg = d3.select("#virtual_spend_top").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");  //(x,y) -> x from left to right, y from top to bottom  
        
        const x = d3.scale.linear()
            .domain([0, d3.max(barchartVals, function (d) {
                return d.value;
            })])
            .range([0, width]);
    
        const y = d3.scale.ordinal()
            .domain(barchartVals.map(function (d) {
                return d.name;
            }))
            .rangeRoundBands([height, 0], .1); // [set the range that our bars will cover], the amount of padding between the bars   
        
        const yAxis = d3.svg.axis()
            .scale(y)
            .tickSize(0)
            .orient("left");

        const gy = svg.append("g")
            .attr("class", "y axis")
            .attr("fill", "white")
            .call(yAxis);

        let bars = svg.selectAll(".bar")
            .data(barchartVals)
            .enter()
            .append("g");        
         
        bars.append("rect")
            .attr("class", "bar")
            .attr("y", function (d) {
                return y(d.name);
            })
            .attr("height", y.rangeBand())
            .attr("x", 0)
            .attr("width", function (d) {
                return x(d.value);
            })
            .attr("fill", function(d) {
                if (d.value == maxVal) {
                    return "grey";  
                } else if (d.value<0) {
                    if (d.value == minVal) {
                        return "tomato"; //tomato or firebrick
                    } else {
                        return "red";
                    }
                } else if (d.value == minVal) {
                    return "chocolate"; 
                }
                return "navy";
            });            
            
        bars.append("text")
            .attr("class", "label")
            .attr("y", function (d) {
                return y(d.name) + y.rangeBand() / 2 + 4;
            })
            .attr("x", function (d) {
                return x(d.value) + 3;
            })
            .text(function (d) {
                return d.value;
            })
            .attr("fill", "white");        
    }
    
    
});
