
(function () {
  'use strict';

  angular.module('OKR.pages.login', [

  ])
    .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
    $stateProvider
      .state('/login', {
        url: '/login',
        templateUrl: 'app/pages/login/login.html',
        controller: 'LoginCtrl'
      })
  }
})();
