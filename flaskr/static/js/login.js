$(document).ready(function(){

    $(".content .panel .register").hide();




    $("#btn_newUser").click(function(){

        let text = $(this).text();

        if(text=="新用户")
        {
            $(".content .panel .register").show();
            $(".content .panel .login").hide();
            $(this).text("返回")
        }
        else
        {
            $(".content .panel .register").hide();
            $(".content .panel .login").show();
            $(this).text("新用户")
        }

        
        return false;
    })

});