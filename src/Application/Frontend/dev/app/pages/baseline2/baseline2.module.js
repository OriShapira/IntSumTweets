
(function () {
  'use strict';

  angular.module('OKR.pages.baseline2', [

  ])
      .config(routeConfig);

  /** @ngInject */
  function routeConfig($stateProvider) {
  	
    $stateProvider
        .state('baseline2', {
          url: '/baseline2',
          templateUrl: 'app/pages/baseline2/baseline2.html',
          controller: 'Baseline2Ctrl'
          
        })
      
  }

})();
