from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import os
from dotenv import load_dotenv
from action_recorder import ActionRecorder

# Carregar variáveis de ambiente
load_dotenv()

class LinkedInBot:
    def __init__(self, learning_mode=False):
        # Configurar opções do Chrome
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        
        # Inicializar o Chrome WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.learning_mode = learning_mode
        
        # Inicializar gravador de ações se estiver em modo de aprendizado
        if learning_mode:
            self.recorder = ActionRecorder(self.driver)
    
    def login(self):
        """Função para fazer login no LinkedIn"""
        try:
            # Abrir página inicial do LinkedIn
            self.driver.get("https://www.linkedin.com")
            time.sleep(3)
            
            if self.learning_mode:
                # Iniciar gravação e aguardar ações do usuário
                self.recorder.start_recording()
                return True
            else:
                # Clicar no botão Entrar
                entrar_button = self.wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "nav__button-secondary"))
                )
                entrar_button.click()
                time.sleep(2)
                
                # Esperar pelos campos de login
                email_field = self.wait.until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                password_field = self.driver.find_element(By.ID, "password")
                
                # Inserir credenciais
                email_field.send_keys(os.getenv('LINKEDIN_EMAIL'))
                time.sleep(1)
                password_field.send_keys(os.getenv('LINKEDIN_PASSWORD'))
                time.sleep(1)
                
                # Clicar no botão de login
                login_button = self.driver.find_element(By.CLASS_NAME, "btn__primary--large")
                login_button.click()
                time.sleep(5)
                return True
            
        except Exception as e:
            print(f"Erro ao fazer login: {str(e)}")
            return False
    
    def close(self):
        """Fechar o navegador"""
        self.driver.quit()

def main():
    # Iniciar em modo de aprendizado na primeira execução
    learning_mode = not os.path.exists("linkedin_actions.json")
    bot = LinkedInBot(learning_mode=learning_mode)
    
    if learning_mode:
        print("Modo de aprendizado ativado!")
        print("O bot irá gravar todas as suas ações.")
    
    # Tentar fazer login
    if bot.login():
        if not learning_mode:
            print("Login realizado com sucesso!")
    else:
        print("Falha ao fazer login")
    
    bot.close()

if __name__ == "__main__":
    main()
