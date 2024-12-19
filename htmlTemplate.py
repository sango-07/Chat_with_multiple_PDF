css = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

body {
    background-color: #f4f6f9;
    font-family: 'Inter', sans-serif;
}

.chat-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.chat-message {
    display: flex;
    margin-bottom: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    transition: all 0.3s ease;
}

.chat-message:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.chat-message.user {
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    color: white;
}

.chat-message.bot {
    background: linear-gradient(135deg, #38ef7d 0%, #11998e 100%);
    color: white;
}

.chat-message .avatar {
    width: 15%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    background-color: rgba(255, 255, 255, 0.1);
}

.chat-message .avatar img {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(255, 255, 255, 0.3);
}

.chat-message .message {
    width: 85%;
    padding: 15px;
    font-size: 1rem;
    line-height: 1.6;
}

.chat-message.user .message {
    text-align: left;
}

.upload-section {
    background-color: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}

.upload-section h3 {
    color: #2575fc;
    margin-bottom: 15px;
}

.stTextInput > div > div > input {
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    padding: 10px;
    font-size: 1rem;
}

.stButton > button {
    background-color: #2575fc !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background-color: #1a5aff !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://i.imgur.com/7zxqQ3y.png" alt="Bot Avatar">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://i.imgur.com/3JbqQAZ.png" alt="User Avatar">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''