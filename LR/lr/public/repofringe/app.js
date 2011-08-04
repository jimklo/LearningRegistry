
var labelType, useGradients, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport 
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

var Log = {
  elem: false,
  write: function(text){
    if (!this.elem) 
      this.elem = document.getElementById('log');
    this.elem.innerHTML = text;
    this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
  }
};


var initGraph = function(model) {
	
	jQuery("#related-keys").html("");
	
	//init RGraph
    window.rgraph = new $jit.RGraph({
        //Where to append the visualization
        injectInto: 'related-keys',
        //Optional: create a background canvas that plots
        //concentric circles.
//        background: {
//          CanvasStyles: {
//            strokeStyle: '#555'
//          }
//        },
        //Add navigation capabilities:
        //zooming by scrolling and panning.
        Navigation: {
          enable: true,
          panning: true,
          zooming: 10
        },
        //Set Node and Edge styles.
        Node: {
            color: '#f00',
            type: 'circle',
            overridable: true
        },
        
        Edge: {
          color: '#C17878',
          lineWidth:1,
          overridable: true
        },
        
        levelDistance: 200,
        
        onBeforeCompute: function(node){
            Log.write("centering " + node.name + "...");
            //Add the relation list in the right column.
            //This list is taken from the data property of each JSON node.
            //$jit.id('inner-details').innerHTML = node.data.relation;
        },
        
        //Add the name of the node in the correponding label
        //and a click handler to move the graph.
        //This method is called once, on label creation.
        onCreateLabel: function(domElement, node){
            domElement.innerHTML = node.name;
            domElement.onclick = function(){
                rgraph.onClick(node.id, {
                    onComplete: function() {
                        Log.write("done");
                    }
                });
            };
        },
        //Change some label dom properties.
        //This method is called each time a label is plotted.
        onPlaceLabel: function(domElement, node){
            var style = domElement.style;
            style.display = '';
            style.cursor = 'pointer';

//            if (node._depth <= 1) {
                style.fontSize = "0.8em";
                style.color = "#ccc";
            
//            } else if(node._depth == 2){
//                style.fontSize = "0.7em";
//                style.color = "#494949";
//            
//            } else {
//                style.display = 'none';
//            }

            var left = parseInt(style.left);
            var w = domElement.offsetWidth;
            style.left = (left - w / 2) + 'px';
        }
    });
    //load JSON data
    window.rgraph.loadJSON(model);
    //trigger small animation
    window.rgraph.graph.eachNode(function(n) {
      var pos = n.getPos();
      pos.setc(-200, -200);
    });
    window.rgraph.compute('end');
    window.rgraph.fx.animate({
      modes:['polar'],
      duration: 2000
    });
	
}



window.cur_related_keys = {};

var relatedKeys = function(envelope) {
	if (envelope.keys) {
		for (var i=0; i<envelope.keys.length; i++) {
			var clean = envelope.keys[i].toLowerCase().trim();
			if (!window.cur_related_keys[clean]) {
				window.cur_related_keys[clean] = 0;
			}
			window.cur_related_keys[clean] += 1;
		}
	}
	
	
}

var keywordModel = function() {
	var template = jQuery("#keywordModelTemplate").html();
	var cur_keys = jQuery("#cur-keys");
	
	var children = "";
	var op = "";
	
	var max = window.cur_related_keys[cur_keys.val()];
	
	for (var key in window.cur_related_keys) {
		if (key == cur_keys.val()) continue;
		children += op + jQuery.mustache(template, {
			"keyword": key,
			"count": window.cur_related_keys[key],
			"children": "",
			"dim": window.cur_related_keys[key]/max
		});
		op = ","
			
	}
	

	var json = jQuery.mustache(template, {
		"keyword": cur_keys.val(),
		"count": window.cur_related_keys[cur_keys.val()],
		"children": children,
		"dim": 1
	});
	
	var obj;
	obj = eval("obj = "+json);
	//console.dir(obj);
	
	return obj;
	
	
}

var displayKeys = function() {
	var related_keys = jQuery("#related-keys");
	var template = jQuery("#relatedKeyTemplate").html();
	related_keys.html("");
	for (var key in window.cur_related_keys) {		
		related_keys.prepend(jQuery.mustache(template, { 
			"related_key": key,
			"count": window.cur_related_keys[key]
		}));
	}
}

var getThumbnail = function(resource_locator) {
	
	var template = jQuery("#thumbnailTemplate").html();
	
	return jQuery.mustache(template, {
		"resource_locator": encodeURIComponent(resource_locator)
	});
}


var handleSlice = function(data) {
	window.cur_related_keys = {};
	window.results = data;
	//console.log(data);
//	for (key in data) {
//		console.log("key:"+key);
//	}
	var template = jQuery("#resourceRowTemplate").html();
	var target = jQuery("#resource_body");
	
	target.html("");
	if (data.documents) {
//		console.log("have documents");
		doc = data.documents;
		for (var i=0; i < data.documents.length; i++) {
			
//			console.dir(doc[i]);
			if (doc[i].resource_data_description && 
					doc[i].resource_data_description.resource_locator) {
//				console.log("locator");
				thumb_url = getThumbnail(doc[i].resource_data_description.resource_locator);
				target.prepend(jQuery.mustache(template, 
					{ 
						"thumbnail": thumb_url,
						"resource_locator_url": doc[i].resource_data_description.resource_locator,
						"identity": (doc[i].resource_data_description.identity ? doc[i].resource_data_description.identity : null)
					} 
				));
				relatedKeys(doc[i].resource_data_description);
			}
			
		}
		
		//displayKeys();
		var keyModel = keywordModel();
		
		initGraph(keyModel);
	}
	
	
}

var doSlice = function() {	
	var keys = jQuery("#keys");
	var cur_keys = jQuery("#cur-keys");

	cur_keys.val(keys.val());
	
	jQuery.getJSON("/slice", { "any_tags": keys.val(), "stale": true, "limit" : 100 }, handleSlice);
}


jQuery(function() {
	jQuery("#search-form").submit(function() {
		doSlice();
		return false;
	})
});