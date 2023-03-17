
(function () {
  'use strict';

  angular.module('OKR.pages.registration', [

  ])
      .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
  	
    $stateProvider
        .state('registration', {
          url: '/registration',
          templateUrl: 'app/pages/registration/registration.html',
          controller: 'RegistrationCtrl'
          
        })
      
  }

})();
