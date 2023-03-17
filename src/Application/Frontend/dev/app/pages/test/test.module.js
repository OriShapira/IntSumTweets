
(function () {
  'use strict';

  angular.module('OKR.pages.test', [

  ])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
  	
    $stateProvider
      .state('test', {
        url: '/test',
        templateUrl: 'app/pages/test/test.html',
        controller: 'TestCtrl'
      })
  }
})();
