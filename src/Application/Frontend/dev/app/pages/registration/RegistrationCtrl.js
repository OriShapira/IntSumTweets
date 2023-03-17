
(function() {'use strict';

  angular.module('OKR.pages.registration')
    .controller('RegistrationCtrl', RegistrationCtrl);

  /** @ngInject */
  function RegistrationCtrl($scope, $rootScope,$location) {
    
    $scope.metaData="You are invited to take part in a research survey about text and event exploring. Your participation will require approximately 60 minutes and is completed online at your computer. There are no known risks or discomforts associated with this survey. Taking part in this study is completely voluntary. If you choose to be in the study you can withdraw at any time without adversely affecting your relationship with anyone at BIU university. Your responses will be kept strictly confidential, and digital data will be stored in secure computer files. Any report of this research that is made available to the public will not include your name or any other individual information by which you could be identified. If you have questions or want a copy or summary of this study’s results, you can contact the researcher at hadarg@gmail.com. Checking the 'I agree' checkbox below indicates that you are 18 years of age or older, and indicates your consent to participate in this survey. Thank you very much for your cooperation."
    
    function init() {
      document.getElementById("ageField").focus();
    }
    
    init();
    
    $scope.start=function(){
    
      //send to server registrationScreenOutput object
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
        "data": "{\"registrationScreenOutput\": {\"userInfo\": {\"agreementAccepted\":"+$scope.registrationScreenOutput.userInfo.agreementAccepted+",\"age\":"+$scope.registrationScreenOutput.userInfo.age+",\"gender\": \""+$scope.registrationScreenOutput.userInfo.gender+"\", \"education\":\""+$scope.registrationScreenOutput.userInfo.education+"\",\"occupation\": \""+$scope.registrationScreenOutput.userInfo.occupation+"\"} },\"clientId\" :\""+$rootScope.clientId+"\"}"
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
