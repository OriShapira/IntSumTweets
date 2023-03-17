
(function () {
  'use strict';

  angular.module('OKR.theme')
    .service('connectGETService',  function($rootScope,$http,$location) {
     var dataStorage;//storage for cache
     
     
     return {fn:function(url) {
     		
	        return dataStorage =  	$http.get($rootScope.baseUrl+url,{
   												/* headers: {'X-CSRF-TOKEN': header}*/
									})
	                         		.then(function (response) {
	              							return response;
	        						},function (err) {
	              							$location.path('/login');
	        						});

    }
    }

});

  /** @ngInject */
  

})();