
(function () {
  'use strict';

  angular.module('OKR.theme')
    .service('connectDELETEService',  function($rootScope,$http,$location) {
     var dataStorage;//storage for cache
    
     
     return {fn:function(url,id) {
     	 
	        return dataStorage =  	$http.delete($rootScope.baseUrl+url+'&id='+id,{
   											/*	headers: {'X-CSRF-TOKEN': header}*/
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