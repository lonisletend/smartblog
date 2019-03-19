function isEmpty(obj){
    if(obj==undefined || obj==null || obj==''){
        return true;
    }
    return false;
}

$("#com-sub").click(function(){
    comment = $("#comment").val();
    if(isEmpty(comment)){
        $.notify({
            title: "错误:",
            message: "评论不能为空！"
        },{
            type: 'danger'
        });
        $("#comment").focus();
        return false;
    }
    if(/<script/.test(comment)){
      $.notify({
            title: "错误:",
            message: "请勿输入特殊标签！"
        },{
            type: 'danger'
        });
        $("#comment").focus();
        return false;
    }

    $.ajax({
      url: '/add_comment',
      data: $('#com-form').serialize(),
      type: 'POST',
      success: function(res){
        if(res.status == true){
          location.reload();
        } else {
          $.notify({
              title: "错误:",
              message: res.msg
          },{
              type: 'danger'
          });
        }
      }
    });

});