/*exported AppConfig*/

// Init the application configuration module for AngularJS application
var AppConfig = (function () {
    // Init module configuration options
    var appModuleDependencies = [
		
	'ui.router',
    	'ui.bootstrap',
	'highcharts-ng',
	'ui.bootstrap.datetimepicker',
	'isteven-multi-select',
    'ui.sortable',
	'ngStorage',
	'angular-growl'];

    // Add a new vertical module
    var registerModule = function (moduleName, dependencies) {
        // Create angular module
        angular.module(moduleName, dependencies || []);

        // Add the module to the AngularJS configuration file
        angular.module('hydroponic').requires.push(moduleName);
    };

    return {
        appModuleName: 'hydroponic',
        appModuleDependencies: appModuleDependencies,
        registerModule: registerModule
    };
})();
