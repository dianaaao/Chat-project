import smtplib, email.message as msg, email.mime.image as img, dotenv, os

dotenv.load_dotenv()
msg_host = os.getenv("MSG_HOST")
msg_port = os.getenv("MSG_PORT")
msg_email = os.getenv("MSG_EMAIL")
msg_password = os.getenv("MSG_PASSWORD")

def send_verification_email(to_email: str, verify_url: str):
    with smtplib.SMTP(host = msg_host, port = int(msg_port)) as smtp:
        smtp.starttls()
        smtp.login(
            user = msg_email,
            password = msg_password  
        )

        email_msg  = msg.EmailMessage()
        
        email_msg["Subject"] = "WorldIT" # задаємо тему нашого листа
        email_msg["From"] = msg_email # вказуємо від кого буде лист
        email_msg["To"] = to_email  # вказує кому буде надходити лист

        email_msg.set_content('Лист підтвердження від WorldIT')

        html = f"""
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <div style="max-width: 600px; margin: 0 auto; padding: 30px 300px; border: 1px solid #999; border-radius: 20px;">

                <h1 style = "margin: 0; font-size: 32px; position: relative; left: 0;">Вас вітає команда World IT !</h1>
                <p style = "font-size: 16px;">Щоб завершити реєстрацію та переконатися, що саме ви є <br> власником цієї електронної адреси, будь ласка, підтвердіть свою <br> пошту.</p>
                
                <a href="{verify_url}" style = "display: inline-block;
                                text-align: center;

                                margin-top: 15px;
                                padding-top: 15px;

                                height: 36px;
                                border: none;
                                border-radius: 5px;
                                background-color: black;
                                color: white;
                                width: 100%;">Підтвердити пошту</a>

                <img src="cid:image1" alt="team" style="display: block; margin: 0 auto; max-width: 100%;"> 

                <hr style = "width: 100%; border: 1px solid #999999; margin: 0;">

                <p style = "font-size: 16px;">Якщо у вас виникнуть питання — ми завжди раді допомогти! <br> З найкращими побажаннями, команда World IT Academy</p>

            </div>
        </body>
        </html>
        """

        email_msg.add_alternative(html, subtype = "html")
        with open("app/static/images/team.png", "rb") as file:
            data = file.read()
            image = img.MIMEImage(data, subtype="png")
            image.add_header("Content-ID", "<image1>")
            email_msg.attach(image)

        smtp.send_message(email_msg)