from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.text import LabelBase
import base64

class EncryptionApp(App):
    def build(self):
        LabelBase.register(name='MicrosoftYaHei', fn_regular='./msyh.ttc')

        self.layout = BoxLayout(orientation='vertical')

        self.input_output = TextInput(hint_text='输入明文或密文', font_name='MicrosoftYaHei')
        self.key_input = TextInput(hint_text='输入密钥', multiline=False, font_name='MicrosoftYaHei')

        self.encrypt_button = Button(text='加密', on_press=self.encrypt_message)
        self.decrypt_button = Button(text='解密', on_press=self.decrypt_message)

        self.result_label = Label(text='结果将在这里显示', font_name='MicrosoftYaHei')

        self.layout.add_widget(self.input_output)
        self.layout.add_widget(self.key_input)
        self.layout.add_widget(self.encrypt_button)
        self.layout.add_widget(self.decrypt_button)
        self.layout.add_widget(self.result_label)

        return self.layout

    def encrypt_message(self, instance):
        try:
            text = self.input_output.text.strip()
            key = self.key_input.text.strip()
            if text and key:
                encrypted_msg = encrypt(text, key)
                self.result_label.text = f'加密结果：{encrypted_msg}'
            else:
                self.result_label.text = "请输入明文或密文以及密钥。"
        except Exception as e:
            self.result_label.text = f"发生错误：{str(e)}"

    def decrypt_message(self, instance):
        try:
            text = self.input_output.text.strip()
            key = self.key_input.text.strip()
            if text and key:
                decrypted_msg = decrypt(text, key)
                self.result_label.text = f'解密结果：{decrypted_msg}'
            else:
                self.result_label.text = "请输入明文或密文以及密钥。"
        except Exception as e:
            self.result_label.text = f"发生错误：{str(e)}"

# 加密函数
def encrypt(msg, key):
    msg = msg.encode('utf-8')
    key = key.encode('utf-8')
    while len(key) < len(msg):
        key += key
    key = key[:len(msg)]
    result = bytearray()
    for i in range(len(msg)):
        result.append(msg[i] ^ key[i])
    return base64.b64encode(result).decode('utf-8')

# 解密函数
def decrypt(msg, key):
    msg = base64.b64decode(msg.encode('utf-8'))
    key = key.encode('utf-8')
    while len(key) < len(msg):
        key += key
    key = key[:len(msg)]
    result = bytearray()
    for i in range(len(msg)):
        result.append(msg[i] ^ key[i])
    return result.decode('utf-8')

if __name__ == '__main__':
    EncryptionApp().run()
