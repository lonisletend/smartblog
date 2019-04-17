  function isEmpty(obj){
    if(obj==undefined || obj==null || obj==''){
      return true;
    }
    return false;
  }

  $("#search-btn").click(function(){
    search();
  })

  function search(){
    stext = $("#search-text").val();
    window.location.href = "/search?q="+stext;
  }