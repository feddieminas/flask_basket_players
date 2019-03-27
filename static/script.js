$(document).ready(function() {
    // materialize js functionalities
    $(".button-collapse").sideNav();
    $('select').material_select();
    $('input#disc1_rate, input#disc2_rate, input#disc3_rate, input#vp_time, input#username, input#password').characterCounter();
    $(".character-counter").css({'color': 'white'});
    $('#modal_edit').modal(); $('#modal_dele').modal();
    
    // sets an issue on large tablets and desktop, thus you make virtual times more linear with rating columns
    if ($('input#vp_time').length) {
        $(window).on('resize', function(){
            $('input#vp_time').css({'width':$('input#disc3_rate').width() + "px", transition: 'width 0.5s ease-in-out 0s'});
        }).resize();
    }
    
    // horizontal table scrolling relative to window's width 
    $("#table-body").scroll(function ()
    {
        let theChange = 0;
        width = $(window).width();
        if (width >= 1850) {
            theChange = ((width-1850)/2) + 285;
        }
        else if (width >= 1000) {
            theChange = (width/1000) * 150;
            if(width >= 1807 && width >= 1849) {
                theChange+=(width-1800) / 7;
            }
        }
        else if (width >= 900) {
            theChange = ((width/900) * 67.5);
        }
        else if (width >= 700) {
            theChange = (width/700) * 52.5;
        }
        else if (width >= 600) {
            theChange = ((width/600) * 30)*1.4;
        }   
        else if (width >= 400) {
            theChange = (width/400) * 20;
        }         
        else if (width >= 300) {
            theChange = (width/300) * 15;
        }          
        
        $("#table-header").offset({ left: (-1*this.scrollLeft)+theChange });
    });
    
    // set table height to be resized with a min value to release vertical scrolling for multi players
    function setTableBody()
    {
        $("#table-body").height(Math.min(500, $("#tbl-container").height() - $("#table-header").height()));
    }

    ////////////////////////////////////////////////
    
    // As a single input of Name is provided, need to check whether a guest will insert both name or surname
    // or only the surname. Apart from a whitespace or a tab, we include the possibility of separate them with dot and comma 
    // (ex. michael jordan - michael.jordan - michael,jordan). 
    function hasNameSurname(s) {return /[,.\s\/]/g.test(s);}
    
    function findSplitSeparator(s) {
        match = /[,.\s\/]/g.exec(s);
        return match[0];
    }
    
    function fitName(nameField) { 
        //trim leftwise
        nameField = nameField.replace(/^\s+/,""); 
        //trim rightwise
        nameField = nameField.replace(/\s$/, "");
        if (hasNameSurname(nameField)) {
            splitNameSurname=nameField.split(findSplitSeparator(nameField));
            theName = splitNameSurname[0].slice(0,1);
            theSurname = splitNameSurname[splitNameSurname.length-1].slice(0,10); 
            nameField = theName + '. ' + theSurname;
        }    
        else {
            nameField=nameField.slice(0,12);     
        }
        return nameField; // max name field characters will be 12 
    }

    if (!$(".player")[0]){
        /* If no any player exists, hide the section body of charts and table. 
        At the same time insert a pulse to the button of adding a player to instruct a guest */        
        $(".visualswitcher").css({'visibility': 'hidden'});
        $('.btn-floating.btn-large').addClass('pulse');
        
    } else {
        /* If any player exists, show the section body of charts and table. 
        At the same time remove the pulse to the button of adding a player to instruct a guest */
        $(".visualswitcher").css({'visibility': 'visible'});
        $('.btn-floating.btn-large').removeClass('pulse');
                
        //// D3 PIE CHART - BIRTH REGION PERCENTAGES - vals through py and jinja  ////        
                
        let piechartVals = [{"label": "Europe","value": 0}, {"label": "America","value": 0}, {"label": "Africa","value": 0},{"label": "Asia","value": 0}
        ,{"label": "Australia","value": 0},{"label": "South Am","value": 0}];
                
        const tableBodyRows = transData.length;
                
        for (let i = 0; i < transData.length; i++) {
            let result = transData[i];
                    
            let birth_region = result["birth_region"];
            let index = piechartVals.findIndex(function(d) {
                return d.label == birth_region;
            });            
            piechartVals[index]["value"]+=1;                    
                    
        }
                
        const f = d3.format(".1f"); 
        piechartVals.map(function(item) {
            item.value = parseFloat(f((item.value/tableBodyRows) *100));
            item.label = item.label.slice(0,4);
            if(item.label=="Sout") {item.label="Sa"}
        });        
        piechartVals = piechartVals.filter(function(d) {
            return d.value>0;
        });
                
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
                
        const thePieChart = d3.select('#birth_region').append("svg:svg")
            .data([piechartVals])
            .attr("width", w)
            .attr("height", h)
            .attr("class", "piechart")
            .append("svg:g")
            .attr("transform", "translate(" + r + "," + r + ")");
                
        const pie = d3.layout.pie().value(function(d){return d.value;});
                
        const arc = d3.svg.arc().outerRadius(r);
                
        let arcs = thePieChart.selectAll("g.slice").data(pie).enter().append("svg:g").attr("class", "slice");
                
        arcs.append("svg:path")
            .attr("fill", function(d, i){return aColor[i];})
            .attr("d", function (d) {return arc(d);});
                
        arcs.append("svg:text")
            .attr("transform", function(d){
                d.innerRadius = 90;
                d.outerRadius = r;
                return "translate(" + arc.centroid(d) + ")";}
            )
            .attr("text-anchor", "middle")
            .attr("font-size", "12px")
            .attr("fill", "white")
            .transition()
            .attr("dx", function(d,i) {
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
            .text( function(d, i) {return piechartVals[i].label.toUpperCase() ;});        


        //// D3 BAR CHART - TOP FIVE PLAYERS GUEST WILLING TO SPEND TIME - vals through html document loaded ////                
                
        let barchartVals = []; 
        let myIndexdict = {"4": "disc1", "5": "disc2", "6": "disc3"}, colT="transparent";
        $('.player').each(function(i, obj) {
            barchartVals.push({"name": $(this).find("td:eq(1)").text(),"value": parseFloat($(this).find("td:eq(8)").text())});  
            
            // while looping through each player, insert the bar rate length rate per layer
            let result = transData[i]["discipline"];
            for (let j=4; j<7; j++) {
                let resultVal = result[myIndexdict[String(j)]][1];
                resultVal = resultVal=="" ? 0 : resultVal;
                let percentFill = Math.min(parseFloat((resultVal*10).toFixed(2)), 100), percentTransp = percentFill;
                let colF1=null, colF2=null;
                switch (j) {
                    case 4:
                        colF1="rgba(175, 132, 27, 0.7)", colF2="rgb(191, 159, 82)";
                        break;
                    case 5:
                        colF1="rgba(115, 114, 114, 0.7)", colF2="rgb(130, 125, 125)"; 
                        break;
                    case 6:
                        colF1="rgba(140, 86, 34, 0.7)", colF2="rgb(195, 109, 6)";
                        break;
                }   
            
                $(this).find("td:eq(" + j + ")").css({background:"-moz-linear-gradient(left,"+colF1+" "+"0%, "+colF2+" "+percentFill+"%," +colT+" "+percentTransp+"%)"});
                $(this).find("td:eq(" + j + ")").css({background:"-webkit-gradient(left top,right top, color-stop(0%,"+colF1+"), color-stop("+percentFill+"%,"+colF2+"), color-stop("+percentTransp+"%,"+colT+"))"});
                $(this).find("td:eq(" + j + ")").css({background:"-webkit-linear-gradient(left,"+colF1+" "+"0%, "+colF2+" "+percentFill+"%," +colT+" "+percentTransp+"%)"});
                $(this).find("td:eq(" + j + ")").css({background:"-o-linear-gradient(left,"+colF1+" "+"0%, "+colF2+" "+percentFill+"%," +colT+" "+percentTransp+"%)"});
                $(this).find("td:eq(" + j + ")").css({background:"-ms-linear-gradient(left,"+colF1+" "+"0%, "+colF2+" "+percentFill+"%," +colT+" "+percentTransp+"%)"});
                $(this).find("td:eq(" + j + ")").css({background:"linear-gradient(to right,"+colF1+" "+"0%, "+colF2+" "+percentFill+"%," +colT+" "+percentTransp+"%)"});
            }
        }); 
                
        valsCount = barchartVals.length;
        if (valsCount>5) {valsCount=5};
                
        barchartVals = barchartVals.sort(function (a, b) {
                return d3.descending(a.value, b.value);
        }).slice(0,valsCount);
                
        barchartVals.map(function(item) {
            item.name = fitName(item.name);
            if (item.value<=0) {item.value=0}
        });       
                
        const maxVal = barchartVals[valsCount-1]["value"];
        const minVal = barchartVals[0]["value"];
                
        const margin = { 
                top: 5,
                right: 45,
                bottom: 0,
                left: 105
            };   
                    
        const width = 450 - margin.left - margin.right;
                
        let height = 50 * barchartVals.length;
        height = height - margin.top - margin.bottom; 
                
        let svg = d3.select("#virtual_spend_top").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .attr("class", "barchart")
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");   
                
        const x = d3.scale.linear()
            .domain([0, d3.max(barchartVals, function (d) {
                return d.value;
            })])
            .range([0, width]);
            
        const y = d3.scale.ordinal()
            .domain(barchartVals.map(function (d) {
                return d.name;
            }))
            .rangeRoundBands([height, 0], .1);  
                
        const yAxis = d3.svg.axis()
            .scale(y)
            .tickSize(0)
            .orient("left");
        
        svg.append("g")
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
                        return "tomato";
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
            .attr("fill", function(d) {
                return "white";
            });                          
            
        // table functionalities to set heights and not fall out of the container    
        setTableBody();
        $(window).resize(setTableBody);
        $("#tbl-container").height($("#table-text-header").height() + $("#table-header").height() + $("#table-body").height() + 65); 
        
    }
    
});
   