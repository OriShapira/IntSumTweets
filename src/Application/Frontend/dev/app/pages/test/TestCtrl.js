
(function() {'use strict';

  angular.module('OKR.pages.test')
    .controller('TestCtrl', TestCtrl);

  /** @ngInject */
  function TestCtrl($scope,$timeout,$rootScope) {
    
    function init() {
    
      $scope.timeEnter=new Date();
    
      $scope.test =  angular.fromJson(window.localStorage['currentScreenInput']);
      $scope.questions = $scope.test.screenObj1.questionsScreenInput.questions;
      //$scope.currentScreenOutput={
      //  screenObj1:{questionsScreenOutput:{answers:[]}},
      //  clientId:$rootScope.clientId
      //}
      $scope.needDirections = $scope.test.needDirections;
      
      $scope.output={
        currentScreenOutput:{
          screenObj1:{questionsScreenOutput:{answers:[]}}
        },
        clientId:$rootScope.clientId
      }
      
      if ($scope.test.timeAllowed && $scope.test.timeAllowed > 0)
      {
        document.getElementById("barIdTest").style.WebkitAnimationDuration = $scope.test.timeAllowed+"s";
        document.getElementById("barIdTest").style.animationDuration = $scope.test.timeAllowed+"s";// Safari, and Opera    
        // time function
        $scope.promise =$timeout(function() {
          $scope.finish=true;
        }, ($scope.test.timeAllowed*1000));
      }
      // if a time limit is not given or is less than or equal to 0:
      else
      {
        document.getElementById("barIdTest").style.WebkitAnimationDuration = "0.5s";
        document.getElementById("barIdTest").style.animationDuration = "0.5s";    // Safari, and Opera    
        $scope.showNextButton=true;
      }
    }
    
    init();
    
    $scope.next=function(status){
      
      document.getElementById("barIdTest").style.WebkitAnimationPlayState = "paused"; // Code for Chrome, Safari, and Opera
      document.getElementById("barIdTest").style.animationPlayState = "paused";
      if (status)
      {
        var timeUse=((new Date().getTime()-$scope.timeEnter.getTime())/ 1000);
      }
      else
      {
        var timeUse=$scope.test.timeAllowed
      }
      
      $scope.output.currentScreenOutput.timeSpentOpen=timeUse;
      //$scope.currentScreenOutput.screenObj1.screenType="questions";
         
      var settings = {
        "async": true,
        "crossDomain": true,
        "url": $rootScope.baseUrl,
        "method": "POST",
        "headers": {
          "content-type":"application/x-www-form-urlencoded" // ,
          //"cache-control": "no-cache",
          //"postman-token": "a9d01218-6db3-5bf9-c354-f73b6d9983bf"
        },
        "processData": false,
        "data": angular.toJson($scope.output) //{currentScreenOutput:$scope.currentScreenOutput})
      }
        
      $.ajax(settings).done(function (response) {
        console.log(response);
        var response=angular.fromJson(response);
        //$scope.currentScreenInput=response.currentScreenInput;
        //$rootScope.routePages($scope.currentScreenInput);
        $rootScope.routePages(response);
      });
    }
    
    // when user clicks next, open a confirmation box:
    $scope.nextOnConfirm=function(status){
      // if user clicks yes, go to 'nextTask' function, otherwise do nothing:
      $scope.doConfirm("Are you sure you would like to go on to the next page?", function yes(){$scope.next(status);}, function no(){});
    }
        
    // confirmation box:
    $scope.doConfirm=function(msg, yesFn, noFn) {
      var confirmBox = $(".modal");
      confirmBox.find(".message").text(msg); // set the message
      confirmBox.find(".yes,.no").unbind().click(function(){confirmBox.css("display", "none");}); // close when yes/no pressed
      confirmBox.find(".yes").click(yesFn); // action for clicking yes
      confirmBox.find(".no").click(noFn); // action for clicking no
      //confirmBox.show();
      confirmBox.css("display", "block"); //show dialog
    }
    
    
  }
})();
