
(function () {
  'use strict';

  angular.module('OKR.theme')
    .service('connectPOSTService',  function($rootScope,$http,$location) {
     var dataStorage;//storage for cache
    
     return {fn:function(url,data) {
     	 	/*var header=localStorage.getItem("authKey");*/
	        return dataStorage =  	$http.post($rootScope.baseUrl+url,data,{
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