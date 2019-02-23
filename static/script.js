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
            theSurname = splitNameSurname[splitNameSurname.length-1].slice(0,10); //Surname 0,8
            nameField = theName + '. ' + theSurname;
        }    
        else {
            nameField=nameField.slice(0,12);     //9
        }
        return nameField; 
    }
    
    //in  the end to isert all
    if (!$(".player")[0]){
        //Do something if class not exists" visibility hidden
        $(".visualswitcher").css({'visibility': 'hidden'});
    } else {
        //"Do something if class exists" visibility true
        $(".visualswitcher").css({'visibility': 'visible'});
        
        queue()
            .defer(d3.json, "static/listChart.json")
            .await(makeGraphs); 
                
            function makeGraphs(error, transData) {
                //console.log(error); //if empty file throws error
                //if (!error) {console.log("jsond", transData)}
                
                if (error) return;
                console.log("jsond", transData);
                
                let piechartValsJSON = [{"label": "Europe","value": 0}, {"label": "America","value": 0}, {"label": "Africa","value": 0},{"label": "Asia","value": 0}
                ,{"label": "Australia","value": 0},{"label": "South Am","value": 0}];
                
                const tableBodyRows = transData.length;
                console.log("rows",tableBodyRows);
                
                for (let i = 0; i < transData.length; i++) {
                    let result = transData[i];
                    //console.log("result", result);
                    
                    //pie chart
                    let birth_region = result["birth_region"];
                    let index = piechartValsJSON.findIndex(function(d) {
                        return d.label == birth_region;
                    });            
                    piechartValsJSON[index]["value"]+=1;                    
                    
                    //bar chart
                    //barchartVals.push({"name": $(this).find("td:eq(1)").text(),"value": parseFloat($(this).find("td:eq(8)").text())});
                    //for(let k in result) {
                       //console.log("k", k, "result[k]", result[k]);
                    //}
                }
                
                console.log("piechartValsJSON",piechartValsJSON);
                
                let barchartValsJSON = [];
                $('.player').each(function(i, obj) {
                    //bar chart
                    barchartValsJSON.push({"name": $(this).find("td:eq(1)").text(),"value": parseFloat($(this).find("td:eq(8)").text())});  
                }); 
                console.log("barchartValsJSON",barchartValsJSON);
                
                /*
                //back up plan the context processor START
                const dictGoforRate = {"brunch": 0.60, "coffee": 0.28, "street": 0.11, "na": 0.01}
                let vpCalcs = 0; let gofor = undefined; let times = undefined;
                
                const f = d3.format(".1f");
                
                let barchartValsJSONBP = [];
                
                for (let i = 0; i < transData.length; i++) {
                    let result = transData[i]["virtual_meet"];
                    for(let k in result) {
                        //console.log("k", k, "result[k]", result[k]);
                        switch(k) {
                            case "go_for":
                                gofor = result[k];
                                break;
                            case "times_see":
                                times= result[k];
                                break;
                            default:
                        }
                    }    
                    
                    let goforResRate = dictGoforRate["na"];
                    if(gofor) {
                        goforResRate = dictGoforRate[gofor]; 
                    }
                    //console.log(goforResRate,times,gofor);
                    
                    vpCalcs=parseFloat(f((((goforResRate * times) * 100)/2.5)));
                    barchartValsJSONBP.push({"name": transData[i]["name"],"value": vpCalcs});
                }
                console.log("barchartValsJSONBP",barchartValsJSONBP);
                
                $('.player').each(function(i, obj) {
                    $(this).find("td:eq(8)").text(barchartValsJSONBP[i]["value"]); //or .val
                });
                //back up plan the context processor END
                */
                
            }        

        //let chartVals= {}; 
        //chartVals.Names = []; chartVals.BR = []; chartVals.VR = [];
        let barchartVals= []; 
        let piechartVals= [{"label": "Europe","value": 0}, {"label": "America","value": 0}, {"label": "Africa","value": 0},{"label": "Asia","value": 0}
        ,{"label": "Australia","value": 0},{"label": "South Am","value": 0}];
        
        //let tableBodyRows = 0;
        const tableBodyRows = $('#myTable tr').length - 1;
        
        $('.player').each(function(i, obj) {
            //console.log(i,obj); /* $(this) */
            
            //pie chart
            let birth_region = $(this).find("td:eq(3)").text();
            let index = piechartVals.findIndex(function(d) {
                return d.label == birth_region;
            });            
            piechartVals[index]["value"]+=1;
            //tableBodyRows+=1;
            
            //bar chart
            barchartVals.push({"name": $(this).find("td:eq(1)").text(),"value": parseFloat($(this).find("td:eq(8)").text())});
            
            //chartVals.Names.push($(this).find("td:eq(1)").text()); //name
            //chartVals.BR.push($(this).find("td:eq(3)").text()); //birth_region
            //chartVals.VR.push($(this).find("td:eq(8)").text()); //virtual_rate
        });
        
        //console.log("rows",tableBodyRows);
        console.log("pie",piechartVals);
        console.log("bar",barchartVals);
        
        //console.log(chartVals["Names"]);
        //console.log(chartVals["BR"]);
        //console.log(chartVals["VR"]); 
        //console.log(chartVals["VR"][0])
        
        //Pie Chart
        const f = d3.format(".1f"); 
        piechartVals.map(function(item) {
            item.value = parseFloat(f((item.value/tableBodyRows) *100));
            item.label = item.label.slice(0,4);
            if(item.label=="Sout") {item.label="Sa"}
        });        
        //console.log("pie",piechartVals);
        
        const w = 300;
        const h = 250;
        const r = Math.min(w, h) / 2;

        const aColor = [
            'rgb(15, 117, 186)',
            'rgb(0, 128, 255)',
            'rgb(101, 147, 245)',
            'rgb(115, 194, 251)',
            'rgb(87, 160, 211)',
            'rgb(149, 200, 216)'
        ]
        
        /*
        const aColor = [
            'rgb(178, 55, 56)',
            'rgb(197, 75, 76)',
            'rgb(214, 100, 85)',
            'rgb(230, 125, 126)',
            'rgb(239, 183, 182)',
            'rgb(241, 71, 73)'
        ]
        */
        
        const thePieChart = d3.select('#birth_region').append("svg:svg")
            .data([piechartVals])
            .attr("width", w)
            .attr("height", h)
            .attr("class", "piechart")
            .append("svg:g")
            .attr("transform", "translate(" + r + "," + r + ")");
        
        const pie = d3.layout.pie().value(function(d){return d.value;});
        
        // Declare an arc generator function
        const arc = d3.svg.arc().outerRadius(r);
        
        // Select paths, use arc generator to draw
        let arcs = thePieChart.selectAll("g.slice").data(pie).enter().append("svg:g").attr("class", "slice");
        arcs.append("svg:path")
            .attr("fill", function(d, i){return aColor[i];})
            .attr("d", function (d) {return arc(d);})
        ;
        
        // Add the text
        arcs.append("svg:text")
            .attr("transform", function(d){
                d.innerRadius = 90;
                d.outerRadius = r;
                return "translate(" + arc.centroid(d) + ")";}
            )
            
            
            .attr("text-anchor", "middle")
            
            .attr("font-size", "12px")
            .attr("fill", "black")
            //.attr("class", function(d) {})
            
            .transition()
            .attr("dx", function(d,i) {
                //console.log(d);
                if (d.data["label"]=="Aust") {
                    return "0.3em";
                }
                else if (d.data["label"]=="Euro") {
                    return "-0.6em";
                }
                else if (d.data["label"]=="Afri") {
                    return "0.5em";
                }
                return "0em";
            })

            .attr("dy", function(d) {
                if (d.data["label"]=="Aust") {
                    return "0.83em";
                }
                return "0.4em";
            }) 
            
            .text( function(d, i) {return piechartVals[i].label.toUpperCase() ;}) //piechartVals[i].value + '%'            
        ;        
        
        ////////////////////////////////////////////////////////////////////
        
        //Bar Chart
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
        
        const margin = { 
                top: 5,
                right: 45,
                bottom: 0,
                left: 105
            };
    
        
        const width = 450 - margin.left - margin.right, height = 250 - margin.top - margin.bottom;    
        
        let svg = d3.select("#virtual_spend_top").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .attr("class", "barchart")
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
   