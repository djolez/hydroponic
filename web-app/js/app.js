//Start by defining the main module and adding the module dependencies
angular.module(AppConfig.appModuleName, AppConfig.appModuleDependencies);

angular.module(AppConfig.appModuleName).config(['$urlRouterProvider', function ($urlRouterProvider) {
    $urlRouterProvider.otherwise("/home");
}]);

//Then define the init function for starting up the application
angular.element(document).ready(function () {
    //Then init the app
    angular.bootstrap(document, [AppConfig.appModuleName]);
});

angular.module(AppConfig.appModuleName).config(['growlProvider', function(growlProvider){
	growlProvider.globalTimeToLive({
		success: 1000,
		warning: 3000	
	});

	growlProvider.globalDisableCountDown(true);
}]);
