var meteoApp = angular.module('meteoApp', ['chart.js','serialport']);

var splib = require('serialport');



Date.prototype.timeNow = function () {
     return ((this.getHours() < 10)?"0":"") + this.getHours() +":"+ ((this.getMinutes() < 10)?"0":"") + this.getMinutes() +":"+ ((this.getSeconds() < 10)?"0":"") + this.getSeconds();
}

meteoApp.controller("meteoCtrl", function($scope) {

    $scope.currentdate = new Date();
    $scope.currenttmp = 0;
    $scope.currenthum = 0;
    $scope.currentpres = 0;
    //temperatureChart
    
    $scope.tempseries = ['Temperature (C)'];
    $scope.tempdata = [[]];
    $scope.templabels = [];
    
    //humidityChart
    
    $scope.humidseries = ['Humidity (%)'];    
    $scope.humiddata = [[]];
    $scope.humidlabels = [];
    
    //pressureChart 
    
    $scope.presseries = ['Pressure (Pa)'];
    $scope.presdata = [[]];
    $scope.preslabels = [];
    
    
    $scope.serialport = new splib.SerialPort('/dev/ttyACM0', {
        baudrate: 9600,
        parser: splib.parsers.readline('\n')
    });
    
    
    $scope.serialport.on('data', function(data) {
        var json = JSON.parse(data); 
        $scope.currenttmp = parseFloat(json.tmp);
        $scope.currenthum = parseFloat(json.hum);
        $scope.currentpres = parseFloat(json.pres);
        var timenow = $scope.currentdate.timeNow();
            $scope.tempdata[0].push($scope.currenttmp);
            $scope.tempdata[0].splice(0,1);
            $scope.templabels.push(timenow);
            $scope.templabels.splice(0,1);    
            $scope.presdata[0].push($scope.currentpres);
            $scope.presdata[0].splice(0,1);      
            $scope.templabels.push(timenow);
            $scope.templabels.splice(0,1);
            $scope.humiddata[0].push($scope.currenthum);
            $scope.humiddata[0].splice(0,1);
            $scope.templabels.push(timenow);
            $scope.templabels.splice(0,1);
            console.log(data);
    });
    
 
  
    /*
    $scope.append_datum = function (datum) {
        
       
            
    }; */
    
    
    $scope.printlog = function(args) {
        for (i = 0; i<args.length; i++) {
            console.log(args[i]);            
        }
    }




});