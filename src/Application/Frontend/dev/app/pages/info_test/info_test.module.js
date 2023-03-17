
(function () {
  'use strict';
  angular.module('OKR.pages.info_test', [

  ])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
  	
    $stateProvider
      .state('info_test', {
        url: '/info_test',
        templateUrl: 'app/pages/info_test/info_test.html',
        controller: 'InfoTestCtrl'
      })
  }
})();
