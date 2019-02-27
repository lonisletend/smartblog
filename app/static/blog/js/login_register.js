
    function isEmpty(obj){
        if(obj==undefined || obj==null || obj==''){
          return true;
        }
        return false;
      }
  
        $('#loginbtn').click(function(){
          var username = $('#username0').val()
          var password = $('#password0').val()
          console.log(username);
          console.log(isEmpty(username));
          if(isEmpty(username) || isEmpty(password)){
            $('#lcomplain').show();
            $('#lcomplain').html('请填写用户名和密码！');
            setTimeout(function(){
              $('#lcomplain').hide();
            }, 5000)
            return;
          }
          $.ajax({
            url: '/login',
            data: $('#loginForm').serialize(),
            type: 'POST',
            success: function(res){
              //console.log(response);
              if(res.status == true){
                $('#lsuccess').show();
                $('#lsuccess').html(res.msg);
                location.reload();
              }else{
                $('#lfail').show();
                $('#lfail').append(res.msg);
                setTimeout(function(){
                  $('#lfail').html('<strong>登录失败：</strong>');
                  $('#lfail').hide();
                }, 5000);
              }
            },
            error: function(error){
              console.log(error);
            }
          })
        })
  
        $('#regbtn').click(function(){
          var username1 = $.trim($('#username1').val());
          var password1 = $.trim($('#password1').val());
          var password2 = $.trim($('#password2').val());
          var email = $.trim($('#email').val());
          var reg = /^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/;
          
          if(isEmpty(username1)){
            $('#rcomplain').show();
            $('#rcomplain').html('用户名不能为空！');
            $('#username1').focus();
            setTimeout(function(){
              $('#rcomplain').hide();
            }, 5000)
            return;
          }
          if(isEmpty(email)){
            $('#rcomplain').show();
            $('#rcomplain').html('邮箱不能为空！');
            setTimeout(function(){
              $('#rcomplain').hide();
            }, 5000)
            return;
          }else if(!reg.test(email)){
            $('#rcomplain').show();
            $('#rcomplain').html('邮箱格式不正确！');
            setTimeout(function(){
              $('#rcomplain').hide();
            }, 5000)
            return;
          }
          if(isEmpty(password1) || isEmpty(password2)){
            $('#rcomplain').show();
            $('#rcomplain').html('密码不能为空！');
            $('#password1').focus();
            setTimeout(function(){
              $('#rcomplain').hide();
            }, 5000)
            return;
          }
          if(password1 != password2){
            $('#rcomplain').show();
            $('#rcomplain').html('两次密码不一致！');
            $('#password1').focus();
            setTimeout(function(){
              $('#rcomplain').hide();
            }, 5000)
            return;
          }
          $.ajax({
            url: '/register',
            data: $('#registrationForm').serialize(),
            type: 'POST',
            success: function(res){
              //console.log(response);
              if(res.status == true){
                $('#rsuccess').show();
                $('#rsuccess').html(res.msg);
                setTimeout(function(){
                  //location.reload();
                  $("#register").modal("hide");
                  $("#register").on("hidden.bs.modal",function(){
                    $("#login").modal("show");
                    $("#register").off().on("hidden","hidden.bs.modal");
                  })
                },3000)
              }else{
                $('#rfail').show();
                $('#rfail').append(res.msg);
                setTimeout(function(){
                  $('#rfail').html('<strong>注册失败：</strong>');
                  $('#rfail').hide();
                }, 5000);
              }
            },
            error: function(error){
              console.log(error);
            }
          })
        })
