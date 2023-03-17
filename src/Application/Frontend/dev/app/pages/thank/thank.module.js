
(function () {
  'use strict';
  angular.module('OKR.pages.thank', [

  ])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
      
    $stateProvider
      .state('thank', {
        url: '/thank',
        templateUrl: 'app/pages/thank/thank.html',
        controller: 'ThankCtrl'  
      })
    }
})();
