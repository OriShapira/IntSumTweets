
(function() {'use strict';

  angular.module('OKR.pages.goodbye')
    .controller('GoodbyeCtrl', GoodbyeCtrl);

  /** @ngInject */
  function GoodbyeCtrl($scope,$rootScope) {
    
    $scope.currentScreenInput = angular.fromJson(window.localStorage['currentScreenInput']);
    
  }

})();
