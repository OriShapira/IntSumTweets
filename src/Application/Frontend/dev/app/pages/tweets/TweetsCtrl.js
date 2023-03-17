
(function() {'use strict';

  angular.module('OKR.pages.tweets')
    .controller('TweetsCtrl', TweetsCtrl);

  /** @ngInject */
  function TweetsCtrl($scope,$timeout,$rootScope) {
    
    function init(){
      $scope.timeEnter=new Date();
      $scope.twitter=angular.fromJson(window.localStorage['currentScreenInput']);
      $scope.twitters=$scope.twitter.screenObj1.baselineScreenInput.tweets;
      $scope.needDirections = $scope.twitter.needDirections;
      // if a time limit is given:
      if ($scope.twitter.timeAllowed && $scope.twitter.timeAllowed > 0)
      {
        document.getElementById("barId").style.WebkitAnimationDuration = $scope.twitter.timeAllowed+"s";
        document.getElementById("barId").style.animationDuration = $scope.twitter.timeAllowed+"s"; // Safari and Opera
        // time function
        $timeout(function() {
          $scope.finish=true;
        }, ($scope.twitter.timeAllowed*1000));
      }
      // if a time limit is not given or is less than or equal to 0:
      else
      {
        document.getElementById("barId").style.WebkitAnimationDuration = "0.5s";
        document.getElementById("barId").style.animationDuration = "0.5s"; // Safari and Opera
        $scope.showNextButton=true;
      }
    }
    
    init();
    
    $scope.next=function(status){
      
      // status:true means that the user finished before the time limit (or there was no time limit)
      // status:false means that the user went over the time limit
      
      document.getElementById("barId").style.WebkitAnimationPlayState = "paused"; // Code for Chrome, Safari, and Opera
      document.getElementById("barId").style.animationPlayState = "paused";
      if (status)
      {
        var timeUse=((new Date().getTime()-$scope.timeEnter.getTime())/ 1000);
      }
      else
      {
        var timeUse=$scope.twitter.timeAllowed
      }
      
      var settings = {
        "async": true,
        "crossDomain": true,
        "url": $rootScope.baseUrl,
        "method": "POST",
        "headers": {
          "content-type":"application/x-www-form-urlencoded" // ,
          //"cache-control": "no-cache",
          //"postman-token": "939069e6-69cc-dbe0-fffe-6a7bf6515736"
        },
        "processData": false,
        "data": "{\"currentScreenOutput\": {\"timeSpentOpen\":"+timeUse+", \"screenObj1\": {\"baselineScreenOutput\": { \"screenType\": \"baseline\" }}},\"clientId\" :\""+$rootScope.clientId+"\"}"
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
