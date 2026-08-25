VERIFYCODEHTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>验证码通知</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8f3e6; font-family: Microsoft YaHei, sans-serif;">
    <div style="max-width: 520px; margin: 40px auto; background-color: var(--primary-color); border-radius: 16px; padding: 36px 30px; box-shadow: 0 6px 22px rgba(58, 37, 26, 0.12);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: var(--secondary-color); font-size: 24px; margin:0; letter-spacing: 1px;">❖ 叶果 ❖</h2>
            <p style="color: #73b436; font-size: 14px; margin-top: 8px;">账号安全验证码</p >
        </div>
        <p style="color: var(--secondary-color); font-size: 15px; line-height: 1.7; margin: 0 0 24px 0;">
            您好！您正在进行账号注册验证操作，本次操作的6位验证码如下，请在5分钟内完成验证：
        </p >
        <div style="background-color: #ffffff; border-left: 6px solid #73b436; border-radius: 10px; padding: 22px 16px; text-align: center; margin-bottom: 26px;">
            <span style="font-size: 36px; font-weight: bold; color: var(--secondary-color); letter-spacing: 6px;">{{CODE}}</span>
        </div>
        <p style="color: var(--secondary-color); font-size: 14px; line-height:1.6; margin:0;">
            ⚠️ 验证码有效期仅5分钟，请勿向他人泄露验证码；<br>
            若并非您本人操作，请忽略此邮件，您的账号不会受到影响。
        </p >
        <div style="height: 1px; background-color: rgba(58, 37, 26, 0.18); margin: 32px 0 20px 0;"></div>
        <p style="text-align:center; font-size:13px; color:#73b436; margin:0;">
            本邮件由系统自动发送，请勿直接回复<br>网站测试用,若因为我输错邮箱地址导致本邮件意外发到您的邮箱,我在此表示歉意,望您原谅
        </p >
    </div>
</body>
</html>
"""
