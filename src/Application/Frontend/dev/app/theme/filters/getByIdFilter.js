
(function () {
  'use strict';

  angular.module('OKR.theme')
  .filter('getByIdFilter', function() {
  return function(arr, id) {
      var obj =   arr.filter(function(item){
							return (item.id === id);
                   })[0]; 
      return arr.indexOf(obj);  			   
			  
  }
})
  .filter('getByIdOptionFilter', function() {
  return function(arr, id) {
      var obj =   arr.filter(function(item){
							return (item.id == id);
                   })[0]; 
      return arr.indexOf(obj);  			   
			  
  }
});
  /** @ngInject */


})();
