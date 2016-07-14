'use strict';

/*global GLOBAL_SETTINGS*/

angular.module('home').config(['$stateProvider',
	function ($stateProvider) {
	    $stateProvider.
		state('home', {
		    url: '/home',
		    templateUrl: 'js/components/home/views/home.view.html',
		    controller: 'homeController'
		});

	}
]);
