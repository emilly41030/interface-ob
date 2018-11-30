/*
 * Parse the data and create a graph with the data.
 */
function parseData(createGraph) {
	Papa.parse("static/train_log_loss.txt", {
		download: true,
		complete: function(results) {
			createGraph(results.data);
		}
	});
}

function createGraph(data) {
	var iter = [];
	var loss = ["loss"];

	for (var i = 0; i < data.length; i++) {
		iter.push(data[i][0]);
		loss.push(data[i][2]);
	}

	console.log(iter);
	console.log(loss);

	var chart = c3.generate({
		bindto: '#chart',
	    data: {
	        columns: [
	        	loss
	        ]
	    },
	    axis: {
	        x: {
	            type: 'category',
	            categories: iter,
	            tick: {
	            	multiline: false,
                	culling: {
                    	max: 15
                	}
            	}
	        }
	    },
	    zoom: {
        	enabled: true
    	},
	    legend: {
	        position: 'right'
	    }
	});
}

parseData(createGraph);