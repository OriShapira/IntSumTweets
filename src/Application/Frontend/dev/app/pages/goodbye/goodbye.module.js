
(function () {
  'use strict';
  angular.module('OKR.pages.goodbye', [

  ])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
      
    $stateProvider
      .state('goodbye', {
        url: '/goodbye',
        templateUrl: 'app/pages/goodbye/goodbye.html',
        controller: 'GoodbyeCtrl'  
      })
    }
})();
