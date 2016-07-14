angular.module('config').controller('configController', ['$scope', '$http', 'growl', function ($scope, $http, growl) {
	
	function getConfig(){
		$http.get('p5000/config').then(function(response){
			console.log('Config: ', response);

			$scope.config = response.data;
		});

	}
	getConfig();

	$scope.saveConfig = function(config){
		
		console.log(config.sensors.list);
		
		config.sensors.updateInterval = parseInt(config.sensors.updateInterval);
		if(isNaN(config.sensors.updateInterval)){
			growl.warning('Update interval must be integer');
			return;
		}
		
		config.sensors.checkValuesInterval = parseInt(config.sensors.checkValuesInterval);
		
		if(isNaN(config.sensors.checkValuesInterval)){
			growl.warning('Monitor interval must be integer');
			return;
		}

		var parseError = false;
		
		config.sensors.list.forEach(function(sensor){
			sensor.desiredValue.min = parseFloat(sensor.desiredValue.min);
			sensor.desiredValue.max = parseFloat(sensor.desiredValue.max);
		
			if(isNaN(sensor.desiredValue.min) || isNaN(sensor.desiredValue.max)){
				parseError = true;
			}
		});

		console.log(config.sensors.list);
		
		if(parseError){
			growl.warning('Failed to parse min/max value for some sensor, it must be a valid float number');
			return;
		}

		
		$http.put('p5000/config', config).then(function(response){
			console.log('Saved config');
			growl.success('Successfully saved');
		});
		
	};
}]);








