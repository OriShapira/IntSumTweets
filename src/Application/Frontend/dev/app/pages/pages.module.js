
(function () {
  'use strict';

  angular.module('OKR.pages', [
    'ui.router',
    'OKR.pages.login',
    'OKR.pages.registration',
    'OKR.pages.thank',
    'OKR.pages.test',
    'OKR.pages.info',
    'OKR.pages.tweets',
    'OKR.pages.baseline2',
    'OKR.pages.baseline2_test',
    'OKR.pages.info_test',
    'OKR.pages.tweets_test',
    'OKR.pages.goodbye'
  ])
    .config(routeConfig).run(function($rootScope,$location,$http) {
         
      $rootScope.baseUrl = "http://localhost:1379/"; //"http://your-server/whatever/";
      $rootScope.clientId = ""; //"clientId123";
      
      function init(){
        
        // set a random client id:
        $rootScope.clientId = "id-"+Math.random().toString(10).substr(2, 16);
        
        //receives from Server
        
        var settings = {
          "async": true,
          "crossDomain": true,
          "url": $rootScope.baseUrl,
          "method": "POST",
          "headers": {
            "content-type": "application/x-www-form-urlencoded",
            //"cache-control": "no-cache",
            //"postman-token": "86232bff-cbe2-0e77-e58f-c75c6aaaa6af"
          },
          "data":"{\"clientId\" :\""+$rootScope.clientId+"\"}"
        }
            
        $.ajax(settings).done(function (response) {
          console.log(response);
          var initObj=angular.fromJson(response)
          $rootScope.initObj=initObj.initObj;
          if ($rootScope.initObj.isUserStudy==false)
          {
            //Client loads the main app according to the given DynamicStoryScreenInput.
            window.localStorage['currentScreenInput'] = angular.toJson($rootScope.initObj);    
            $location.path('/info');
          }
          else if ($rootScope.initObj.isUserStudy==true)
            $location.path('/login');
        });
      }
      
      init();
       
      $rootScope.routePages=function(response){
          
        // if response is null, just go to the home page:
        if (!response)
        {
          $location.path('/login');$rootScope.$apply();
        }
        
        else if (response.currentScreenInput)
        {
          var currentScreenInput=response.currentScreenInput;
          window.localStorage['currentScreenInput'] = angular.toJson(currentScreenInput);                                                                        
          
          if(currentScreenInput.screenObj1)
          {
            if (currentScreenInput.screenObj1.baselineScreenInput&&!currentScreenInput.screenObj2){
              $location.path('/tweets');$rootScope.$apply();
            }
            else if (currentScreenInput.screenObj1.questionsScreenInput&&!currentScreenInput.screenObj2){
              $location.path('/test');$rootScope.$apply();
            }
            else if (currentScreenInput.screenObj1.baselineScreenInput&&currentScreenInput.screenObj2.questionsScreenInput){
              $location.path('/tweets_test');$rootScope.$apply();
            }
            else if (currentScreenInput.screenObj1.finishScreenInput&&!currentScreenInput.screenObj2){
              $location.path('/thank');$rootScope.$apply();
            }
            else if (currentScreenInput.screenObj1.dynamicStoryScreenInput&&!currentScreenInput.screenObj2){
              $location.path('/info');$rootScope.$apply();
            }
            else if (currentScreenInput.screenObj1.dynamicStoryScreenInput&&currentScreenInput.screenObj2.questionsScreenInput){
              $location.path('/info_test');$rootScope.$apply();
            }
            else if (currentScreenInput.screenObj1.baseline2ScreenInput&&!currentScreenInput.screenObj2){
              $location.path('/baseline2');$rootScope.$apply();
            }
            else if (currentScreenInput.screenObj1.baseline2ScreenInput&&currentScreenInput.screenObj2.questionsScreenInput){
              $location.path('/baseline2_test');$rootScope.$apply();
            }
          }
          else if (currentScreenInput.goodbye) {
            $location.path('/goodbye');$rootScope.$apply();
          }
        }
        else if (response.error) {
          alert("Error: "+response.error)
        }
        
      }
    });

    /** @ngInject */
    function routeConfig($urlRouterProvider) {
      $urlRouterProvider.otherwise('/login');
    }
})();