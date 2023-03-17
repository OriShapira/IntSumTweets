
(function () {
  'use strict';

  angular.module('OKR.pages.tweets', [

  ])
      .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
  	
    $stateProvider
        .state('tweets', {
          url: '/tweets',
          templateUrl: 'app/pages/tweets/tweets.html',
          controller: 'TweetsCtrl'
          
        })
      
  }

})();
