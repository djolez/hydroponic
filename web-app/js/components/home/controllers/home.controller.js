angular.module('home').controller('homeController', ['$scope', '$http', '$timeout', '$localStorage', '$uibModal', '$window',  function ($scope, $http, $timeout, $localStorage, $uibModal, $window) {

	var defaultHighchartsOptions = {
		chart: {
			type: 'line',
			height: 300,
		},
		plotOptions: {
			line:{
				marker:{
					enabled: false
				}
			}
		}
	}; 

	$scope.selectedSensors = [];
	$scope.config = {};
	$scope.moment = moment;

	$scope.camera = {
		width: 1920,
		height: 1080
	};

	$scope.sortableOptions = {
		stop: function(){
			console.log('STOP: ', $scope.selectedSensors);
		}
	};

	function setDates(){
		var now = new Date();
		$scope.dates = {
			startDate: moment(now).subtract(3, 'hours').toDate(),
			endDate: now
		};

		$scope.timelapse = {
			start: moment(now).hour(7).minute(0).toDate(),
			end: now
		};
	}
	
	$scope.config.datePicker = {
		showMeridian: false
	};	

	$scope.printDate = function(){
		console.log($scope.dates.startDate);
	};
	
	$scope.loaders = {};
	
	var selectedSensors = $localStorage.selectedSensors;

	function selectSensorsFromStorage(list){
		list.forEach(function(sensor){
			sensor.selected = selectedSensors[sensor.name];
		});
		
	}


	$scope.getSensorData = function(startDate, endDate){
		$localStorage.selectedSensors = $scope.output;

		var s = moment(startDate).format('YYYY-MM-DD HH[:]mm[:]ss');
		var e = moment(endDate).format('YYYY-MM-DD HH[:]mm[:]ss');
		
		$scope.selectedSensors = [];

		$scope.availableSensors.forEach(function(sensor){
			if(sensor.selected){
				$scope.loaders.getSensorData = true;
				
				$http.get('/p5000/sensors/' + sensor.name + '?start_date=' + s + '&end_date=' + e).then(function(response){
					console.log('GET_SENSOR_DATA: ', response);

					var values = [];
					var time = [];

					response.data.data.forEach(function(item){
						var date = new Date(item.timestamp);
						date = moment(date).subtract(2, 'hours');

						time.push(moment(date).format('HH[:]mm'));
						 
						values.push(item.value);
					});
				
					var options = angular.copy(defaultHighchartsOptions);
					options.xAxis = { categories: time };
					options.title = { text: sensor.name };

					$scope.selectedSensors.push({
						name: sensor.name,
						config: {
							options: options,
							series: [{ data: values }]
						}
					});
					
					$scope.loaders.getSensorData = false;
					$scope.redrawCharts();
				});
			}
		});
	}

	function deleteSensorData(sensor){
		$scope.selectedSensors.forEach(function(item, index){
			if(item.name === sensor.name){
				$scope.selectedSensors.splice(index, 1);
			}
		});	
	}

	$scope.sensorToggle = function(sensor){
		console.log('SENSOR_TOGGLE: ', sensor);

		if(sensor.selected){
			getSensorData(sensor);
		} else{
			deleteSensorData(sensor);	
		}
	};
	
	function getSensorsList(){
		$http.get('p5000/sensors/list').then(function(response){
			console.log('LIST: ', response);

			$scope.availableSensors = response.data.data;
			selectSensorsFromStorage($scope.availableSensors);
			console.log('selected: ', $scope.availableSensors);

		});
	}

	function getSensorStats(){
		$scope.loaders.getSensorStats = true;

		$http.get('p5000/sensors/stats').then(function(response){
			console.log('Last values: ', response);
			$scope.sensorStats = response.data.data;
			$scope.loaders.getSensorStats = false;
		});
	}

	function getDevices(){
		$scope.loaders.getDevices = true;
		console.log($scope.loaders);

		$http.get('p5000/devices').then(function(response){
			console.log('DEVICES: ', response);
			$scope.devices = response.data.data;

			$scope.devices.forEach(function(device){
				switch(device.name){
					case 'light': 
						device.icon = 'lightbulb-o';
						break;
					case 'water_pump':
						device.icon = 'flask';
						break;
					case 'flash':
						device.icon = 'flash';
						break;

				}
			});
			$scope.loaders.getDevices = false;
		});
	}

	function getLastDeviceActions(){
		$scope.loaders.getLastDeviceActions = true;

		$http.get('p5000/devices/actions').then(function(response){
			console.log('DEVICE ACTIONS: ', response);

			response.data.data.forEach(function(device){
				device.timestamp = moment(device.timestamp).subtract(2, 'hours');
			});

			$scope.deviceActions = response.data.data;
			$scope.loaders.getLastDeviceActions = false;
		});
	}

	function getNotifications(){
		$scope.loaders.getNotifications = true;

		$http.get('p5000/notifications').then(function(response){
			$scope.notifications = response.data.data;
			$scope.loaders.getNotifications = false;
		});
	}

	$scope.initializeData = function(){
		setDates();
		getSensorsList();
		getSensorStats();
		getDevices();
		getLastDeviceActions();
		getNotifications();
	};
	
	$scope.sensorSelected = function(item){
		console.log('Item selected: ', item);
	};

	function executeCommand(device){
		console.log('Execute action: ', device);

		$http.get('p5000/devices/' + device.name + '/' + (device.state === 'on' ? 'off' : 'on') + (device.runTime ? ('?runTime=' + device.runTime) : '')).then(function(response){
			console.log('SWITCH: ', response);
			device.state = (device.state === 'on') ? 'off' : 'on';
			device.runTime = null;
		});
	}

	$scope.sendCommandToDevice = function(device){

		if(device.name === 'water_pump' && device.state === 'off'){
			device.runTime = 15;
			$scope.selectedDevice = device;

			var modalInstance = $uibModal.open({
				templateUrl: 'deviceModal.html',
				controller: 'homeController',
				scope: $scope
			});
			
			$scope.ok = function(){
				executeCommand(device);
				modalInstance.close();
			};

			$scope.cancel = function(){
				modalInstance.dismiss();
			};
			
		} else{
			executeCommand(device);
		}
	}
	
	$scope.takePicture = function(){
		$scope.loaders.takePicture = true;

		$http.get('p5000/camera/take-picture?width=' + $scope.camera.width + '&height=' + $scope.camera.height).then(function(response){
			console.log('Picture taken');
			$scope.loaders.takePicture = false;
			$window.open('/img/' + response.data.name);
		});
	
	}
	
	$scope.openTimelapse = function(start, end){
		$scope.loaders.openTimelapse = true;
		
		var s = moment(start).format('YYYY-MM-DD HH[:]mm[:]ss');
		var e = moment(end).format('YYYY-MM-DD HH[:]mm[:]ss');
	
		$http.get('p5000/camera/open-timelapse?start=' + s + '&end=' + e).then(function(response){
			
			$scope.loaders.openTimelapse = false;
			
			response.data.data.forEach(function(img){
				$window.open('/img/timelapse/' + img);
			});
		});
	}

	$scope.refresh = function(){
		setDates();
		getSensorStats();
		getDevices();
		getLastDeviceActions();
		getNotifications();

		$scope.getSensorData($scope.dates.startDate, $scope.dates.endDate);	
	};

	$scope.redrawCharts = function(){
		$timeout(function(){ $scope.$broadcast('highchartsng.reflow'); }, 10);
	};



}]);



