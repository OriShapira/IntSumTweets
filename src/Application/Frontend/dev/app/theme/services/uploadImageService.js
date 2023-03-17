
(function () {
  'use strict';

  angular.module('OKR.theme')
    .service('uploadImageService',  function($http,$rootScope) {
     var dataStorage;//storage for cache

     return {fn:function(url,fd) {
   
        var header=localStorage.getItem("authKey");
        return dataStorage = $http.post($rootScope.baseUrl+url,fd,{
        									 headers: {
   												 	'Content-Type': undefined,
   												 	'X-CSRF-TOKEN': header}
									})
			                         .then(function (response) {
							              return response;
							        },function (err) {
								             $location.path('/login');
								     });
        
        
        /*
         $.ajax({
                                       url:$rootScope.baseUrl+url,
                                       data: fd,
                                       contentType: false,
                                       processData: false,
                                       type: 'POST',
                                       success: function(response){
                                           return response;
                                       },
                                       error: function(response){
                                          return response;
                                       }     
           });*/
        

    }
    }

});

  /** @ngInject */
  

})();