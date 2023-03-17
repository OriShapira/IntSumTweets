
(function () {
  'use strict';

  angular.module('OKR.pages.info', [

  ])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    
    $stateProvider
      .state('info', {
        url: '/info',
        templateUrl: 'app/pages/info/info.html',
        controller: 'InfoCtrl'
      })
  }
})();
