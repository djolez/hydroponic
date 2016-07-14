'use strict';

/*global GLOBAL_SETTINGS*/

angular.module('config').config(['$stateProvider',
	function ($stateProvider) {
	    $stateProvider.
		state('config', {
		    url: '/config',
		    templateUrl: 'js/components/config/views/config.view.html',
		    controller: 'configController'
		});

	}
]);
