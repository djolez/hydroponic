angular.module('root').controller('rootController', ['$scope', '$state', function ($scope, $state) {

    $state.go('index');
}]);