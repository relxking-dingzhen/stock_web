function bindEmailCaptchaClick() {
    const captchaBtn = document.getElementById('captcha-btn');
    
    captchaBtn.addEventListener('click', function(event) {
        // 阻止默认事件
        event.preventDefault();
        
        // 获取email输入值
        const emailInput = document.querySelector('input[name="email"]');
        const email = emailInput.value;
        
        // 验证邮箱是否填写
        if (!email) {
            alert("请先输入邮箱！");
            return;
        }
        
        // 验证邮箱格式
        if (!/^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$/.test(email)) {
            alert("请输入正确的邮箱格式！");
            return;
        }
        
        // 发送请求
        fetch(`/stocker/captcha/email?email=${email}`)
            .then(response => response.json())
            .then(result => {
                const code = result.code;
                if (code === 200) {
                    let countdown = 60;
                    // 禁用按钮
                    captchaBtn.disabled = true;
                    
                    const timer = setInterval(() => {
                        captchaBtn.textContent = `${countdown}秒`;
                        countdown -= 1;
                        
                        if (countdown <= 0) {
                            clearInterval(timer);
                            captchaBtn.textContent = "获取验证码";
                            captchaBtn.disabled = false;
                        }
                    }, 1000);
                } else {
                    alert(result.message || "发送失败，请稍后重试");
                }
            })
            .catch(error => {
                console.error("发送验证码失败：", error);
                alert("发送失败，请稍后重试");
            });
    });
}

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', () => {
    bindEmailCaptchaClick();
});