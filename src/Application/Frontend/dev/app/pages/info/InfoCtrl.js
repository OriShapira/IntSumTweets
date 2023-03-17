
(function() {'use strict';

  angular.module('OKR.pages.info')
    .controller('InfoCtrl', InfoCtrl);

  /** @ngInject */
  function InfoCtrl($scope,$timeout,$rootScope) {
  
    //to use the Math js function in angular 
    $scope.Math = window.Math;
        
    //PERCENT        
    Array.prototype.sum = function (prop) {
      var total = 0
      for (var i = 0, _len = this.length; i < _len; i++)
      {
        total += this[i][prop]
      }
      return total
    }
            
    //$scope.sum=0;
    
    //$scope.percentCalc=function(numPercent,state){
    //  if(state)
    //  {
    //    //$scope.sum=$scope.sum+Math.floor(numPercent*100);
    //    $scope.sum=$scope.sum+(numPercent*100);
    //  }
    //  else
    //  {
    //    //$scope.sum=$scope.sum-Math.floor(numPercent*100);
    //    $scope.sum=$scope.sum-(numPercent*100);
    //  }
    //}   
    
    $scope.openAllCards=function() {
      var i=0;
      angular.forEach($scope.sentences,function(item){
        if($scope.sentences[i][0].showOnInit==false&&$(".close-card"+i+" table").css('display') == 'none')
        {
          $scope.openclosecards(i, false);
        }
        i=i+1;
      });
      //$scope.calculateTotalSum();
    }
    
    $scope.closeAllCards=function() {
      var i=0;
      angular.forEach($scope.sentences,function(item){
        //if($scope.sentences[i][0].showOnInit==false&&$(".close-card"+i+" table").css('display') == 'block')
        if($scope.sentences[i][0].showOnInit==false&&$(".close-card"+i+" table").css('display') == 'table')
        {
          $scope.openclosecards(i, false);
        }
        i=i+1;
      });
      //$scope.calculateTotalSum();
    }
    
    //$scope.calculateTotalSum=function() {
    //  var i=0;
    //  var totSum=0;
    //  angular.forEach($scope.sentences,function(item){
    //    // count up the sum of the always-open cards and the ones opened manually:
    //    if($scope.sentences[i][0].showOnInit==true)
    //    {
    //      totSum=totSum+$scope.sentences[i].sum("scoreSentence")*100;
    //    }
    //    else if($(".close-card"+i+" table").css('display') != 'none')
    //    {
    //      totSum=totSum+$scope.sentences[i].sum("scoreSentence")*100;
    //    }
    //    i=i+1;
    //  });
    //  $scope.sum=totSum;
    //}
    
    $scope.openclosecards=function(index) {//, needCalculateTotal) {
      //$("#sum1").css("border", "0.08em solid #3cc786");
      //$("#sum2").css("border", "0.08em solid #3cc786");
      
      if($(".close-card"+index+" table").css('display') == 'none')
      {
        //$(".close-card"+index+" table").css("display", "block");
        $(".close-card"+index+" table").css("display", "table");
        //$(".close-card"+index+" table").css("table-layout", "fixed").css("width", "100%");
        $(".close-card"+index).css("margin", "0px 0px 10px 0");
        $(".status-strip"+index).css("display", "none");
        $("#fa"+index).removeClass("fa-angle-down");$("#fa"+index).addClass("fa-angle-up");
        //ממקם את המספר של הכרטיסים הסגורים מתחת כשהם פתוחים
        $(".amount"+index).addClass("amountOpen");$(".amount"+index).removeClass("amountClose");$(".amount"+index).removeClass("amountCloseUsed");
        
        // make keywords invisible when foldable cards are unfolded:
        $(".keywords"+index).css("visibility", "hidden");
      }
      else
      {
        //$(".close-card"+index+" table").css("display", "none");$(".status-strip"+index).css("display", "block");
        $(".close-card"+index+" table").css("display", "none");
        $(".close-card"+index).css("margin", "0px 0px -10px 0");
        $(".status-strip"+index).css("display", "table");
        $("#fa"+index).removeClass("fa-angle-up");$("#fa"+index).addClass("fa-angle-down");
        //ממקם את המספר של הכרטיסים הסגורים מתחתם כשהם פתוחים
        $(".amount"+index).addClass("amountCloseUsed");$(".amount"+index).removeClass("amountOpen");
        
        // make keywords visible when foldable cards are folded:
        $(".keywords"+index).css("visibility", "visible");
        
        delete $scope.index;
      }
      //if (needCalculateTotal)
      //{
      //  $scope.calculateTotalSum();
      //}
    }
    
    
    function init() {
      
      $scope.timeEnter=new Date();
      $scope.info =  angular.fromJson(window.localStorage['currentScreenInput']);
      $scope.dynamicStoryScreenInput = $scope.info.screenObj1?$scope.info.screenObj1.dynamicStoryScreenInput:$scope.info.dynamicStoryScreenInput;
      $scope.needDirections = $scope.info.needDirections;
      
      if ($scope.info.timeAllowed && $scope.info.timeAllowed > 0)
      {
        document.getElementById("barIdInfo").style.WebkitAnimationDuration = $scope.info.timeAllowed+"s";
        document.getElementById("barIdInfo").style.animationDuration = $scope.info.timeAllowed+"s";// Safari, and Opera    
        // time function
        $timeout(function() {
          $scope.finish=true;
        }, ($scope.info.timeAllowed*1000));
      }
      // if a time limit is not given or is less than or equal to 0:
      else
      {
        document.getElementById("barIdInfo").style.WebkitAnimationDuration = "0.5s";
        document.getElementById("barIdInfo").style.animationDuration = "0.5s";    // Safari, and Opera    
        $scope.showNextButton=true;
      }
      
      $scope.sentences=[];
      $scope.keywords=[];
      var sentGroupIdx=-1;
      //var status=$scope.dynamicStoryScreenInput.sentences[0].showOnInit;
      //$scope.sentences[sentGroupIdx]=[];
      var sentenceIsShown=null;
      angular.forEach($scope.dynamicStoryScreenInput.sentences, function(item) {
          
        // a change in folding of sentences:
        if (sentenceIsShown==null || sentenceIsShown!=item.showOnInit)
        {
          // go on to the next group of sentences (folded or unfolded):
          sentGroupIdx=sentGroupIdx+1;
          $scope.sentences[sentGroupIdx]=[];
          sentenceIsShown=item.showOnInit;
          
          // if the new sentence group is not to show on init, add the keywords to that group:
          if (sentenceIsShown==false)
          {
            $scope.keywords[sentGroupIdx] = getKeywordsForGroupBySentenceId(item.id);
          }
        }
          
        item.sentencesarr=item.sentence.split(' ').map(function(word,wordIdx){
          var obj;
          //item.entailmentItems=[];
          
          // look for the current word (in the sentence) in the pressable tokens list:
          angular.forEach(item.pressableTokens,function(token){
            ////אוביקט שיש לו קוד וסוג אותו דבר
            //var index1=$scope.dynamicStoryScreenInput.entailmentItems.findIndex(x => x.id==token.item.id && x.type==token.item.type);
            //if(index1&&index1!=-1)
            //  item.entailmentItems.push(index1);
            
            // if the current pressable token has the index of the word, use it:
            if (token.tokens.indexOf(wordIdx)!=-1)
            {
              // the word has other mentions to corefer to, and also a dictionary entry
              //if (index1 && index1!=-1)
              if (token.expansion)
              {
                obj={
                  word:word,
                  //item:token.item,
                  item:token.conceptId, // the concept ID of the pressable token
                  brothers:token.tokens, // the indices of all the words in this pressable token
                  //dictName:$scope.dynamicStoryScreenInput.entailmentItems[index1].name,
                  //dictDesc:$scope.dynamicStoryScreenInput.entailmentItems[index1].desc
                  dictName:word,
                  dictDesc:token.expansion
                }
              }
              // the word has other mentions to corefer to, but not a dictionary entry
              else
              {
                obj={
                  word:word,
                  //item:token.item,
                  item:token.conceptId, // the concept ID of the pressable token
                  brothers:token.tokens // the indices of all the words in this pressable token
                }
              }
            }
          });
          
          if(!obj)
            obj={word:word};
        
          return obj;
        });
        
        //if(item.showOnInit!=sentenceIsShown)
        //{
        //  // go on to the next group of sentences:
        //  sentGroupIdx=sentGroupIdx+1;
        //  $scope.sentences[sentGroupIdx]=[];
        //  sentenceIsShown=item.showOnInit;
        //}
        
        $scope.sentences[sentGroupIdx].push(item);
        //if(sentenceIsShown)
        //{
        //  //$scope.sum=$scope.sum+Math.floor(item.scoreSentence*100);
        //  $scope.sum=$scope.sum+(item.scoreSentence*100);
        //}
      });
      
      // if needDirections is false, then replace the "next task" button with a "home" button:
      if ($scope.needDirections)
      {
        $scope.nextButtonTxt = "Next Task";
      }
      else
      {
        $scope.nextButtonTxt = "Home";
      }
    }
    
    function getKeywordsForGroupBySentenceId(sentId) {
        var keywordsString = '';
        // go through the keywords groups to find the one with the specified sentence ID:
        angular.forEach($scope.dynamicStoryScreenInput.foldKeywords, function(keywordsInfo) {
            // found the group:
            //alert();
            if (keywordsInfo.ids.indexOf(sentId) != -1)
            {
                keywordsString = keywordsInfo.keywords.join(', ');
            }
        });
        return keywordsString;
    }

    $scope.keywordsWidthPerc = function(keywordsIndex){
      // Returns the width of the specified keywords div as a percentage of its parent container's width.
      // Since the style is set to 50% max, and afterwards to show an elipsis, we only need to show
      // the tooltip when the text is cut with the elipsis.
      var el = document.getElementById("groupKeywords"+keywordsIndex);
      var elParent = el.parentElement;
      return el.clientWidth/elParent.clientWidth;
    }

    $scope.pressToken=function(parentparentindex,parentindex,index,word){
      if(word.item)
      {
        // if the word pressed is the already pressed item, un-highlight it:
        if ($scope.compare(word.item, $scope.item))
        {
          delete $scope.item;
          $scope.bolds=[];
        }
        // otherwise highlight the item and its brother tokens
        else
        {
          $scope.item=word.item;
          $scope.bolds=[];
          $scope.bolds[parentparentindex]=[];
          $scope.bolds[parentparentindex][parentindex]=[];
          //if pressable press all the words in tokens array
          angular.forEach(word.brothers,function(i){
            $scope.bolds[parentparentindex][parentindex][i]=true;
          });
        }
      }
    }    
    
    $scope.compare=function(item1,item2){
      return angular.equals(item1,item2);
    }
        
    $scope.openalert=function(index){
      if($scope.index!=index)//מניעת כפל ביצועים
      {
        $scope.index=index;
        console.log(index);
        $scope.openclosecards(index, true);
      }
      return true;
    }
      
    $scope.nextTask=function(status){
      
      // if the next button is a home button, redirect back home:
      if ($scope.nextButtonTxt == "Home")
      {
        $rootScope.routePages(null); // null tells the routePages function to go to the home page
      }
      
      else
      {
        document.getElementById("barIdInfo").style.WebkitAnimationPlayState = "paused"; // Code for Chrome, Safari, and Opera
        document.getElementById("barIdInfo").style.animationPlayState = "paused";
        if (status)
        {
          var timeUse=((new Date().getTime()-$scope.timeEnter.getTime())/ 1000);
        }
        else
        {
          var timeUse=$scope.info.timeAllowed
        }
        
        var settings = {
          "async": true,
          "crossDomain": true,
          "url": $rootScope.baseUrl,
          "method": "POST",
          "headers": {
            "content-type":"application/x-www-form-urlencoded" // ,
            //"cache-control": "no-cache",
            //"postman-token": "939069e6-69cc-dbe0-fffe-6a7bf6515736"
          },
          "processData": false,
          "data": "{\"currentScreenOutput\": {\"timeSpentOpen\": "+timeUse+", \"screenObj1\":{\"dynamicStoryScreenOutput\": {} } } ,\"clientId\" :\""+$rootScope.clientId+"\"}"
        }
          
        $.ajax(settings).done(function (response) {
          console.log(response);
          var response=angular.fromJson(response);
          //$scope.currentScreenInput=response.currentScreenInput?response.currentScreenInput:response;
          //$rootScope.routePages($scope.currentScreenInput);
          $rootScope.routePages(response);
        });
      }
    }
    
    $scope.hoverIn=function(index){
      ////במידה והכרטיסים סגורים
      //if($(".close-card"+index+" table").css('display') == 'none')
      //{
        ////open cards add percent to sum
        ////var sum=Math.floor($scope.sentences[index].sum("scoreSentence")*100);
        //var sum=$scope.sentences[index].sum("scoreSentence")*100;
        //if($scope.sentences[index].percent)
        //{
        //  Object.keys($scope.sentences[index].percent).forEach(function(key) {
        //    // percent[key]=$scope.sentences[index].percent[key];
        //    if($scope.sentences[index].percent[key])//if details open plus scoreExtraInfo
        //    {
        //      //sum=sum+Math.floor($scope.sentences[index][key].scoreExtraInfo*100);
        //      sum=sum+($scope.sentences[index][key].scoreExtraInfo*100);
        //    }
        //  });
        //}
        ////סכימה לסכום הכללי את מספר האחוזים שיראו כרטיסים אלו
        //$scope.sum=$scope.sum+sum;
        //$("#sum1").css("border", "0.08em solid red");
        //$("#sum2").css("border", "0.08em solid red");
      //}
      $scope.hover=true;
    }
    
    
    $scope.hoverOut=function(index){
      ////במידה והכרטיסים סגורים
      if($(".close-card"+index+" table").css('display') == 'none')
      {
      //  //open cards add percent to sum
      //  //var sum=Math.floor($scope.sentences[index].sum("scoreSentence")*100);
      //  var sum=$scope.sentences[index].sum("scoreSentence")*100;
      //  if($scope.sentences[index].percent)
      //  {
      //    Object.keys($scope.sentences[index].percent).forEach(function(key) {
      //      // percent[key]=$scope.sentences[index].percent[key];
      //      if($scope.sentences[index].percent[key])//if details open plus scoreExtraInfo
      //      {
      //        //sum=sum+Math.floor($scope.sentences[index][key].scoreExtraInfo*100);
      //        sum=sum+($scope.sentences[index][key].scoreExtraInfo*100);
      //      }
      //    });
      //  }
      //  //הפחתה מהסכום הכללי את מספר האחוזים שיראו כרטיסים סגורים אלו
      //  $scope.sum=$scope.sum-sum;
      //  $("#sum1").css("border", "0.08em solid #3cc786");
      //  $("#sum2").css("border", "0.08em solid #3cc786");    
        delete $scope.hover;
      }
    }
            
    
    $scope.closecards=function () {
      $(".close-card table").css("display", "none");
      $(".status-strip").css("display", "block");
      // $(".card table").toggle(200);
      // $(".close-card").removeClass("close-card");
      // $(".status-strip").removeClass("status-strip");
      // $(".all-close").css("padding-bottom", "30px");
      // $(".fa-angle-down").css("transform", "rotate(180deg)");
      // $(".amount").css("bottom", "-0px");
      // $(".amount").css({
      //   width:'-0px!important',
      //   top:'inherit'
      // });
    }
        
    init();
    
    // when user clicks next, open a confirmation box:
    $scope.nextOnConfirm=function(status){
        
      var questionStr = "Are you sure you would like to go on to the next page?";
      if ($scope.nextButtonTxt == "Home")
      {
        questionStr = "Are you sure you would like to leave this page?";
      }
        
      // if user clicks yes, go to 'nextTask' function, otherwise do nothing:
      $scope.doConfirm(questionStr, function yes(){$scope.nextTask(status);}, function no(){});
    }
        
    // confirmation box:
    $scope.doConfirm=function(msg, yesFn, noFn) {
      var confirmBox = $(".modal");
      confirmBox.find(".message").text(msg); // set the message
      confirmBox.find(".yes,.no").unbind().click(function(){confirmBox.css("display", "none");}); // close when yes/no pressed
      confirmBox.find(".yes").click(yesFn); // action for clicking yes
      confirmBox.find(".no").click(noFn); // action for clicking no
      //confirmBox.show();
      confirmBox.css("display", "block"); //show dialog
    }

  }
})();
