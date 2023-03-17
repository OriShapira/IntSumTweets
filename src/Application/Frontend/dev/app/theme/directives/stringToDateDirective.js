/**
 *
 */
(function () {
  'use strict';

  angular.module('OKR.theme')
	  .filter('stringToDate',function(){
    	return function(input){
    		var date=new Date(input);
    		if ( Object.prototype.toString.call(date) === "[object Date]" ) {
				  // it is a date
				  if ( isNaN( date.getTime() ) ) {  // d.valueOf() could also work
				    // date is not valid
				     return 0;
				  }
				  else {
				    // date is valid
				    return date;
				  }
				}
				else {
				  // not a date
				  return 0;
				}
    		}
    		})


})();