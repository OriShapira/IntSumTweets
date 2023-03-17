
(function () {
  'use strict';

  angular.module('OKR.pages.login')
    .controller('LoginCtrl', LoginCtrl);

  /** @ngInject */
  function LoginCtrl($scope,$rootScope,$http,$location,$state) {
    
    function init() {
      document.getElementById("usernameField").focus();
    }
    
    init();
    
    $scope.login=function(){
      
      //Client To Server---Checking
      var settings = {
        "async": true,
        "crossDomain": true,
        "url": $rootScope.baseUrl,
        "method": "POST",
        "headers": {
          "content-type":"application/x-www-form-urlencoded" // "application/json"
        },
        "processData": false,
        "data": "{\"signInScreenOutput\": { \"user\": \""+$scope.signInScreenOutput.user+"\", \"password\":\""+$scope.signInScreenOutput.password+"\"},\"clientId\" :\""+$rootScope.clientId+"\"}"
      }
      var loc = $location;
      
      $.ajax(settings).done(function (response) {
        console.log(response);
        var response=angular.fromJson(response);
        var signInScreenAuthorization=response.signInScreenAuthorization;
        //2 options:
        // {"signInScreenAuthorization":{ "authorized":false }}
        // {"signInScreenAuthorization":{ "authorized":true, "registrationScreenInput": { "message":<string for registration>, "needRegistration":[true|false] }}}

        if (signInScreenAuthorization.authorized==true)
        {
          if (signInScreenAuthorization.registrationScreenInput.needRegistration==true)
          {
            $location.path('/registration');
            $scope.$apply();
          }
          else
          {
            //send to server an empty registrationScreenOutput object since registreation is not needed:
            var settings = {
              "async": true,
              "crossDomain": true,
              "url": $rootScope.baseUrl,
              "method": "POST",
              "headers": {
                "content-type": "application/x-www-form-urlencoded"//,
                //"cache-control": "no-cache",
                //"postman-token": "ac496083-fe56-8011-f918-becae323a811"
              },
              "processData": false,
              "data": "{\"registrationScreenOutput\": {},\"clientId\" :\""+$rootScope.clientId+"\"}"
            }
            // get back from server the next page to go to:
            $.ajax(settings).done(function (response) {
              console.log(response);
              var response=angular.fromJson(response);
              //$scope.currentScreenInput=response.currentScreenInput;
              //$rootScope.routePages($scope.currentScreenInput);
              $rootScope.routePages(response);
            });
          }
        }
        else if (signInScreenAuthorization.authorized==false)
        {
          alert("The username or password are invalid.");
        }
      });
      
      //Authorization from Server
      
    }
    
    $scope.openDemo=function(demoName) {
      $scope.signInScreenOutput={
        user:'demo'+demoName,
        password:'1234'
      }
      //$scope.signInScreenOutput.user = 'demo'+demoName;
      //$scope.signInScreenOutput.password = '1234';
      
      $scope.login();
    }
  }
})();
