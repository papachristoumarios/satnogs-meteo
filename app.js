var meteoApp = angular.module('meteoApp', ['chart.js']);

meteoApp.controller("meteoCtrl", function($scope) {


    $scope.series = ["Temperature"];
    $scope.data = [[12,12,32]];

    $scope.labels = ["A", "B", "C"];





});