
(function() {'use strict';

  angular.module('OKR.pages.thank')
    .controller('ThankCtrl', ThankCtrl);

  /** @ngInject */
  function ThankCtrl($scope,$rootScope) {
    $scope.thank = angular.fromJson(window.localStorage['currentScreenInput']);
    $scope.finishScreenInput = $scope.thank.screenObj1?$scope.thank.screenObj1.finishScreenInput:$scope.thank;
    
    $scope.next=function(){
        
      var settings = {
        "async": true,
        "crossDomain": true,
        "url": $rootScope.baseUrl,
        "method": "POST",
        "headers": {
          "content-type":"application/x-www-form-urlencoded"//,
          //"cache-control": "no-cache",
          //"postman-token": "dc7815a8-00fb-0fbc-7500-259a5c629c4d"
        },
        "processData": false,
        "data": "{\"currentScreenOutput\": {\"timeSpentOpen\":-1, \"screenObj1\":{\"finishScreenOutput\": {} } },\"clientId\" :\""+$rootScope.clientId+"\" }"
      }
      
      $.ajax(settings).done(function (response) {
        console.log(response);
        var response=angular.fromJson(response);
        //$scope.currentScreenInput=response.currentScreenInput;
        //$rootScope.routePages($scope.currentScreenInput);
        $rootScope.routePages(response);
      });
    }
    
    $scope.finish=function(){
      
      // replace newlines with spaces
      $scope.feedbackmsg = $scope.feedbackmsg.replace(/\n/g, " ");
      
      var settings = {
        "async": true,
        "crossDomain": true,
        "url": $rootScope.baseUrl,
        "method": "POST",
        "headers": {
          "content-type":"application/x-www-form-urlencoded"//,
          //"cache-control": "no-cache",
          //"postman-token": "dc7815a8-00fb-0fbc-7500-259a5c629c4d"
        },
        "processData": false,
        "data": "{\"currentScreenOutput\": {\"timeSpentOpen\": -1, \"screenObj1\":{\"finishScreenOutput\": {\"feedback\":\""+$scope.feedbackmsg+"\" } } },\"clientId\" :\""+$rootScope.clientId+"\" }"
      }
        
      $.ajax(settings).done(function (response) {
        console.log(response);
        var response=angular.fromJson(response);
        //$scope.currentScreenInput=response.currentScreenInput;
        //$rootScope.routePages($scope.currentScreenInput);
        $rootScope.routePages(response);
      });
    }
    
  }

})();
