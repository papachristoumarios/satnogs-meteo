var meteoApp = angular.module('meteoApp', ['chart.js','serialport']);





Date.prototype.timeNow = function () {
     return ((this.getHours() < 10)?"0":"") + this.getHours() +":"+ ((this.getMinutes() < 10)?"0":"") + this.getMinutes() +":"+ ((this.getSeconds() < 10)?"0":"") + this.getSeconds();
}

meteoApp.controller("meteoCtrl", function($scope) {

    $scope.SerialPort = require('serialport').SerialPort;
    $scope.serialPort = new $scope.SerialPort('/dev/ttyACM0', {
        baudrate: 115200,
        parser: $scope.SerialPort.parsers.readline('\n')
    });
    
    
    $scope.serialPort.on('data', function(data) {
        $scope.append_datum(data);       
    });
    
    $scope.currentdate = new Date();
    
    //temperatureChart
    
    $scope.tempseries = ['Temperature (C)'];
    $scope.tempdata = [[]];
    $scope.templabels = [];
    
    //humidityChart
    
    $scope.humidseries = ['Humidity (RH)'];    
    $scope.humiddata = [[]];
    $scope.humidlabels = [];
    
    //pressureChart 
    
    $scope.presseries = ['Pressure (Pa)'];
    $scope.presdata = [[]];
    $scope.preslabels = [];
    
    $scope.append_datum = function (datum) {
        
        if (datum.substr(-2) === ' C') {
            datum = parseFloat(datum.substr(datum.length - 3));
            $scope.tempdata[0].push(datum);
            $scope.tempdata[0].splice(0,1);
            
            $scope.templabels.push($scope.currentdate.timeNow());
            $scope.templabels.splice(0,1);
            
        } else-if (datum.substr(-3) === ' Pa') {
            datum = parseFloat(datum.substr(datum.length - 4));
            $scope.presdata[0].push(datum);
            $scope.presdata[0].splice(0,1);
            
            $scope.templabels.push($scope.currentdate.timeNow());
            $scope.templabels.splice(0,1);
        } else-if (datum.substr(-3) === ' RH') {
            datum = parseFloat(datum.substr(datum.length - 4));
            $scope.humiddata[0].push(datum);
            $scope.humiddata[0].splice(0,1);
    
            $scope.templabels.push($scope.currentdate.timeNow());
            $scope.templabels.splice(0,1);
        }
            
    };
    
    
    $scope.printlog = function(args) {
        for (i = 0; i<args.length; i++) {
            console.log(args[i]);            
        }
    }




});