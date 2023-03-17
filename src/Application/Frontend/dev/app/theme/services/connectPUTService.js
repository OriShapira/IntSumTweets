
(function () {
  'use strict';

  angular.module('OKR.theme')
    .service('connectPUTService',  function($rootScope,$http,$location) {
     var dataStorage;//storage for cache
     
     return {fn:function(url,id,data) {
     		
	        return dataStorage =  	$http.put($rootScope.baseUrl+url,data,{
   												/*headers: {'X-CSRF-TOKEN': header}*/
									})
	                         .then(function (response) {
				                if (typeof data == 'object') 
				                     return response;
						              return JSON.parse(response);
						        },function (err) {
						                
						              $location.path('/login');
						        });

    }
    }

});

  /** @ngInject */
  

})();