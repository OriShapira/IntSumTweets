/**
 * Change top "Daily Downloads", "Active Users" values with animation effect
 */
(function () {
  'use strict';

  angular.module('OKR.theme')
     .directive('stringToNumber', function() {
		  return {
		    require: 'ngModel',
		    link: function(scope, element, attrs, ngModel) {
		      ngModel.$parsers.push(function(value) {
		        return '' + value;
		      });
		      ngModel.$formatters.push(function(value) {
		        return parseFloat(value);
		      });
		    }
		  };
	})


})();