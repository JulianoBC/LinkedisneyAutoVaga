from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import time
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class BotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LinkedIn Bot")
        self.root.geometry("800x400")
        
        # Variáveis de controle
        self.is_running = False
        self.skip_current = False
        self.bot = None
        self.bot_thread = None
        self.message_queue = queue.Queue()
        
        # Lista de etapas do bot com funções correspondentes
        self.steps = [
            ("1. Inicializar navegador", self.start_from_init),
            ("2. Fazer login no LinkedIn", self.start_from_login),
            ("3. Navegar para página de vagas", self.start_from_jobs),
            ("4. Buscar por 'Desenvolvedor'", self.start_from_search),
            ("5. Aplicar filtro de candidatura simplificada", self.start_from_filter),
            ("6. Processar lista de vagas", self.start_from_process_jobs),
            ("7. Clicar em vaga", self.start_from_click_job),
            ("8. Verificar botão de candidatura", self.start_from_apply),
            ("9. Preencher formulário", self.start_from_form),
            ("10. Enviar candidatura", self.start_from_submit),
            ("11. Próxima vaga/página", self.start_from_next)
        ]
        self.current_step = 0
        
        self.setup_gui()
        self.update_gui()

    def setup_gui(self):
        # Container principal
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame da lista de etapas (coluna esquerda)
        steps_frame = ttk.LabelFrame(main_container, text="Etapas do Bot (Clique para iniciar)", padding="5")
        steps_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Lista de etapas com scrollbar
        steps_canvas = tk.Canvas(steps_frame, width=200)
        steps_scrollbar = ttk.Scrollbar(steps_frame, orient="vertical", command=steps_canvas.yview)
        steps_scrollable_frame = ttk.Frame(steps_canvas)
        
        steps_scrollable_frame.bind(
            "<Configure>",
            lambda e: steps_canvas.configure(scrollregion=steps_canvas.bbox("all"))
        )
        
        steps_canvas.create_window((0, 0), window=steps_scrollable_frame, anchor="nw")
        steps_canvas.configure(yscrollcommand=steps_scrollbar.set)
        
        # Adicionar etapas como botões clicáveis
        self.step_buttons = []
        for i, (step_text, step_func) in enumerate(self.steps):
            button = ttk.Button(
                steps_scrollable_frame,
                text=step_text,
                command=lambda f=step_func: self.start_from_step(f),
                style='Step.TButton'
            )
            button.pack(pady=2, anchor="w", fill=tk.X)
            self.step_buttons.append(button)
        
        steps_canvas.pack(side=tk.LEFT, fill=tk.Y)
        steps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Estilo para botões de etapa
        style = ttk.Style()
        style.configure('Step.TButton', anchor='w', padding=5)
        
        # Frame principal (coluna direita)
        main_frame = ttk.Frame(main_container)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Status atual
        ttk.Label(main_frame, text="Status Atual:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(main_frame, text="Aguardando início...")
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Log de ações
        ttk.Label(main_frame, text="Log de Ações:").grid(row=1, column=0, columnspan=2, sticky=tk.W)
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=50)
        self.log_text.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Frame de botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Botões
        self.start_button = ttk.Button(button_frame, text="Iniciar", command=self.start_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(button_frame, text="Pausar", command=self.pause_bot, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.restart_button = ttk.Button(button_frame, text="Reiniciar", command=self.restart_bot, state=tk.DISABLED)
        self.restart_button.pack(side=tk.LEFT, padx=5)
        
        self.next_action_button = ttk.Button(button_frame, text="Próxima Ação", command=self.skip_action, state=tk.DISABLED)
        self.next_action_button.pack(side=tk.LEFT, padx=5)

    def update_current_step(self, step_index):
        """Atualiza a etapa atual na lista"""
        # Resetar todas as etapas para cor normal
        for label in self.step_buttons:
            label.configure(foreground="black")
        
        # Destacar etapa atual
        if 0 <= step_index < len(self.step_buttons):
            self.step_buttons[step_index].configure(foreground="blue")
            self.current_step = step_index

    def log_message(self, message):
        self.message_queue.put(message)
        
        # Atualizar etapa atual baseado na mensagem
        step_keywords = {
            "Iniciando": 0,
            "login": 1,
            "página de vagas": 2,
            "Buscando": 3,
            "filtro": 4,
            "lista de vagas": 5,
            "Processando vaga": 6,
            "candidatura": 7,
            "formulário": 8,
            "Candidatura enviada": 9,
            "próxima": 10
        }
        
        for keyword, step in step_keywords.items():
            if keyword.lower() in message.lower():
                self.update_current_step(step)
                break
    
    def update_gui(self):
        # Processar mensagens da fila
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        self.root.after(100, self.update_gui)
    
    def skip_action(self):
        """Pular para a próxima ação"""
        self.skip_current = True
        self.log_message("Pulando para próxima ação...")
        self.next_action_button.config(state=tk.DISABLED)
        time.sleep(0.5)  # Pequena pausa para atualizar interface
        self.next_action_button.config(state=tk.NORMAL)

    def start_from_step(self, step_func):
        """Inicia o bot a partir de uma etapa específica"""
        if self.is_running:
            self.log_message("Por favor, pause ou reinicie o bot antes de mudar a etapa")
            return
            
        self.log_message(f"Iniciando a partir da etapa selecionada...")
        self.start_bot(step_func)

    def start_bot(self, step_func=None):
        if not self.is_running:
            self.is_running = True
            self.skip_current = False
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)
            self.next_action_button.config(state=tk.NORMAL)
            self.status_label.config(text="Iniciando...")
            
            # Iniciar bot em uma thread separada
            if step_func:
                self.bot_thread = threading.Thread(target=step_func)
            else:
                self.bot_thread = threading.Thread(target=self.run_bot)
            self.bot_thread.daemon = True
            self.bot_thread.start()
    
    def pause_bot(self):
        if self.is_running:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.NORMAL)
            self.next_action_button.config(state=tk.DISABLED)
            self.status_label.config(text="Pausado")
            self.log_message("Bot pausado")

    def restart_bot(self):
        """Reiniciar o bot do zero"""
        # Primeiro para o bot atual se estiver rodando
        if self.is_running:
            self.is_running = False
            self.skip_current = False
            self.log_message("Parando bot atual...")
            time.sleep(2)
        
        # Fecha o navegador se existir
        if self.bot:
            try:
                self.bot.close()
            except:
                pass
            self.bot = None
        
        # Limpa o log
        self.log_text.delete(1.0, tk.END)
        self.log_message("Reiniciando bot...")
        
        # Reseta os botões
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.restart_button.config(state=tk.NORMAL)
        self.next_action_button.config(state=tk.NORMAL)
        
        # Inicia novo bot
        self.is_running = True
        self.status_label.config(text="Reiniciando...")
        
        # Inicia nova thread
        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()
    
    def run_bot(self):
        try:
            self.bot = LinkedInBot(self.log_message, self)  # Passa a referência da GUI
            
            # Login
            self.status_label.config(text="Fazendo login...")
            if self.bot.login():
                self.log_message("Login realizado com sucesso!")
                
                # Buscar vagas
                if not self.is_running:
                    return
                    
                self.status_label.config(text="Buscando vagas...")
                if self.bot.buscar_vagas():
                    self.log_message("Busca de vagas realizada com sucesso!")
                    
                    # Candidatar-se às vagas
                    if not self.is_running:
                        return
                        
                    self.status_label.config(text="Candidatando-se às vagas...")
                    if self.bot.candidatar_vagas():
                        self.log_message("Processo de candidatura finalizado!")
                    else:
                        self.log_message("Erro no processo de candidatura")
                else:
                    self.log_message("Erro na busca de vagas")
            else:
                self.log_message("Falha ao fazer login")
        
        except Exception as e:
            self.log_message(f"Erro: {str(e)}")
        finally:
            if not self.is_running:  # Se foi pausado
                return
            
            if self.bot:
                self.bot.close()
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.NORMAL)
            self.next_action_button.config(state=tk.DISABLED)
            self.status_label.config(text="Finalizado")
    
    def run(self):
        self.root.mainloop()

    # Funções para iniciar de diferentes etapas
    def start_from_init(self):
        self.bot = LinkedInBot(self.log_message, self)
        self.run_bot_steps(start_step=0)

    def start_from_login(self):
        self.bot = LinkedInBot(self.log_message, self)
        self.run_bot_steps(start_step=1)

    def start_from_jobs(self):
        self.bot = LinkedInBot(self.log_message, self)
        self.bot.driver.get("https://www.linkedin.com")
        time.sleep(2)
        self.run_bot_steps(start_step=2)

    def start_from_search(self):
        self.bot = LinkedInBot(self.log_message, self)
        self.bot.driver.get("https://www.linkedin.com/jobs/")
        time.sleep(2)
        self.run_bot_steps(start_step=3)

    def start_from_filter(self):
        self.bot = LinkedInBot(self.log_message, self)
        self.bot.driver.get("https://www.linkedin.com/jobs/search/?keywords=Desenvolvedor")
        time.sleep(2)
        self.run_bot_steps(start_step=4)

    def start_from_process_jobs(self):
        self.bot = LinkedInBot(self.log_message, self)
        self.bot.driver.get("https://www.linkedin.com/jobs/search/?keywords=Desenvolvedor&f_AL=true")
        time.sleep(2)
        self.run_bot_steps(start_step=5)

    def start_from_click_job(self):
        self.start_from_process_jobs()  # Começa da lista de vagas

    def start_from_apply(self):
        self.start_from_process_jobs()  # Começa da lista de vagas

    def start_from_form(self):
        self.start_from_process_jobs()  # Começa da lista de vagas

    def start_from_submit(self):
        self.start_from_process_jobs()  # Começa da lista de vagas

    def start_from_next(self):
        self.start_from_process_jobs()  # Começa da lista de vagas

    def run_bot_steps(self, start_step=0):
        """Executa as etapas do bot a partir de um ponto específico"""
        try:
            if start_step <= 1:
                if not self.bot.login():
                    return

            if start_step <= 2:
                self.bot.driver.get("https://www.linkedin.com/jobs/")
                time.sleep(3)

            if start_step <= 3:
                if not self.bot.buscar_vagas():
                    return

            if start_step <= 4:
                if not self.bot.aplicar_filtros():
                    return

            if start_step <= 5:
                if not self.bot.candidatar_vagas():
                    return

        except Exception as e:
            self.log_message(f"Erro: {str(e)}")
        finally:
            if not self.is_running:  # Se foi pausado
                return
            
            if self.bot:
                self.bot.close()
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.NORMAL)
            self.next_action_button.config(state=tk.DISABLED)
            self.status_label.config(text="Finalizado")

class LinkedInBot:
    def __init__(self, log_callback, gui=None):
        # Configurar opções do Chrome
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        
        # Inicializar o Chrome WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.log = log_callback
        self.gui = gui
        
    def check_skip(self):
        """Verifica se deve pular a ação atual"""
        if self.gui and self.gui.skip_current:
            self.gui.skip_current = False  # Reset flag
            return True
        return False

    def login(self):
        """Fazer login no LinkedIn"""
        try:
            # Abrir página inicial do LinkedIn
            self.driver.get("https://www.linkedin.com")
            time.sleep(3)
            
            # Clicar no botão Entrar
            entrar_button = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "nav__button-secondary"))
            )
            entrar_button.click()
            time.sleep(2)
            
            # Preencher credenciais
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
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
            self.log(f"Erro ao fazer login: {str(e)}")
            return False

    def buscar_vagas(self, cargo="Desenvolvedor"):
        """Buscar vagas de desenvolvedor"""
        try:
            # Ir para a página de vagas
            self.log("Navegando para a página de vagas...")
            self.driver.get("https://www.linkedin.com/jobs/")
            time.sleep(5)  # Aumentado para carregar completamente

            # Tentar diferentes seletores para o campo de busca
            search_field = None
            search_selectors = [
                (By.CLASS_NAME, "jobs-search-box__text-input"),
                (By.CLASS_NAME, "jobs-search-box__input"),
                (By.XPATH, "//input[contains(@class, 'jobs-search-box')]"),
                (By.XPATH, "//input[@aria-label='Pesquisar cargo, competência ou empresa']"),
                (By.XPATH, "//input[contains(@placeholder, 'cargo')]")
            ]

            for selector_type, selector in search_selectors:
                try:
                    search_field = self.wait.until(
                        EC.presence_of_element_located((selector_type, selector))
                    )
                    if search_field:
                        self.log("Campo de busca encontrado!")
                        break
                except:
                    continue

            if not search_field:
                self.log("Não foi possível encontrar o campo de busca")
                return False

            # Limpar e preencher campo de busca
            search_field.clear()
            time.sleep(1)
            search_field.send_keys(cargo)
            time.sleep(1)
            search_field.send_keys(Keys.RETURN)
            time.sleep(5)  # Aumentado para carregar resultados

            # Tentar diferentes seletores para o botão de filtros
            filters_button = None
            filter_selectors = [
                (By.XPATH, "//button[contains(@aria-label, 'Filtros')]"),
                (By.XPATH, "//button[contains(., 'Filtros')]"),
                (By.XPATH, "//button[contains(@class, 'filter')]")
            ]

            for selector_type, selector in filter_selectors:
                try:
                    filters_button = self.wait.until(
                        EC.element_to_be_clickable((selector_type, selector))
                    )
                    if filters_button:
                        self.log("Botão de filtros encontrado!")
                        break
                except:
                    continue

            if not filters_button:
                self.log("Não foi possível encontrar o botão de filtros")
                return False

            filters_button.click()
            time.sleep(3)

            # Tentar diferentes seletores para candidatura simplificada
            easy_apply = None
            easy_apply_selectors = [
                (By.XPATH, "//label[contains(., 'Candidatura simplificada')]"),
                (By.XPATH, "//span[contains(text(), 'Candidatura simplificada')]"),
                (By.XPATH, "//label[contains(., 'Easy Apply')]")
            ]

            for selector_type, selector in easy_apply_selectors:
                try:
                    easy_apply = self.wait.until(
                        EC.element_to_be_clickable((selector_type, selector))
                    )
                    if easy_apply:
                        self.log("Opção de candidatura simplificada encontrada!")
                        break
                except:
                    continue

            if not easy_apply:
                self.log("Não foi possível encontrar a opção de candidatura simplificada")
                return False

            easy_apply.click()
            time.sleep(2)

            # Tentar diferentes seletores para o botão mostrar resultados
            show_results = None
            show_results_selectors = [
                (By.XPATH, "//button[contains(., 'Mostrar')]"),
                (By.XPATH, "//button[contains(., 'resultados')]"),
                (By.XPATH, "//button[contains(@class, 'show-results')]")
            ]

            for selector_type, selector in show_results_selectors:
                try:
                    show_results = self.wait.until(
                        EC.element_to_be_clickable((selector_type, selector))
                    )
                    if show_results:
                        self.log("Botão mostrar resultados encontrado!")
                        break
                except:
                    continue

            if not show_results:
                self.log("Não foi possível encontrar o botão mostrar resultados")
                return False

            show_results.click()
            time.sleep(5)  # Aumentado para carregar resultados
            
            self.log("Busca de vagas concluída com sucesso!")
            return True

        except Exception as e:
            self.log(f"Erro ao buscar vagas: {str(e)}")
            return False

    def aplicar_filtros(self):
        """Aplicar filtros de candidatura simplificada"""
        try:
            # Tentar diferentes seletores para o botão de filtros
            filters_button = None
            filter_selectors = [
                (By.XPATH, "//button[contains(@aria-label, 'Filtros')]"),
                (By.XPATH, "//button[contains(., 'Filtros')]"),
                (By.XPATH, "//button[contains(@class, 'filter')]")
            ]

            for selector_type, selector in filter_selectors:
                try:
                    filters_button = self.wait.until(
                        EC.element_to_be_clickable((selector_type, selector))
                    )
                    if filters_button:
                        self.log("Botão de filtros encontrado!")
                        break
                except:
                    continue

            if not filters_button:
                self.log("Não foi possível encontrar o botão de filtros")
                return False

            filters_button.click()
            time.sleep(3)

            # Tentar diferentes seletores para candidatura simplificada
            easy_apply = None
            easy_apply_selectors = [
                (By.XPATH, "//label[contains(., 'Candidatura simplificada')]"),
                (By.XPATH, "//span[contains(text(), 'Candidatura simplificada')]"),
                (By.XPATH, "//label[contains(., 'Easy Apply')]")
            ]

            for selector_type, selector in easy_apply_selectors:
                try:
                    easy_apply = self.wait.until(
                        EC.element_to_be_clickable((selector_type, selector))
                    )
                    if easy_apply:
                        self.log("Opção de candidatura simplificada encontrada!")
                        break
                except:
                    continue

            if not easy_apply:
                self.log("Não foi possível encontrar a opção de candidatura simplificada")
                return False

            easy_apply.click()
            time.sleep(2)

            # Tentar diferentes seletores para o botão mostrar resultados
            show_results = None
            show_results_selectors = [
                (By.XPATH, "//button[contains(., 'Mostrar')]"),
                (By.XPATH, "//button[contains(., 'resultados')]"),
                (By.XPATH, "//button[contains(@class, 'show-results')]")
            ]

            for selector_type, selector in show_results_selectors:
                try:
                    show_results = self.wait.until(
                        EC.element_to_be_clickable((selector_type, selector))
                    )
                    if show_results:
                        self.log("Botão mostrar resultados encontrado!")
                        break
                except:
                    continue

            if not show_results:
                self.log("Não foi possível encontrar o botão mostrar resultados")
                return False

            show_results.click()
            time.sleep(5)  # Aumentado para carregar resultados
            
            self.log("Filtros aplicados com sucesso!")
            return True

        except Exception as e:
            self.log(f"Erro ao aplicar filtros: {str(e)}")
            return False

    def candidatar_vagas(self):
        """Candidatar-se às vagas encontradas"""
        try:
            # Esperar a lista de vagas carregar
            time.sleep(5)
            
            # Tentar diferentes seletores para encontrar a lista de vagas
            job_list = None
            job_list_selectors = [
                (By.CLASS_NAME, "jobs-search-results__list"),
                (By.CLASS_NAME, "jobs-search-results-list"),
                (By.XPATH, "//ul[contains(@class, 'jobs-search')]"),
                (By.XPATH, "//div[contains(@class, 'jobs-search-results-list')]")
            ]

            for selector_type, selector in job_list_selectors:
                try:
                    job_list = self.wait.until(
                        EC.presence_of_element_located((selector_type, selector))
                    )
                    if job_list:
                        self.log("Lista de vagas encontrada!")
                        break
                except:
                    continue

            if not job_list:
                self.log("Não foi possível encontrar a lista de vagas")
                return False

            # Encontrar todas as vagas na lista
            job_cards = None
            job_card_selectors = [
                (By.CLASS_NAME, "job-card-container"),
                (By.CLASS_NAME, "jobs-search-results__list-item"),
                (By.XPATH, "//li[contains(@class, 'jobs-search-results__list-item')]"),
                (By.XPATH, "//div[contains(@class, 'job-card-container')]")
            ]

            for selector_type, selector in job_card_selectors:
                try:
                    job_cards = job_list.find_elements(selector_type, selector)
                    if job_cards:
                        self.log(f"Encontradas {len(job_cards)} vagas!")
                        break
                except:
                    continue

            if not job_cards:
                self.log("Não foi possível encontrar os cartões de vagas")
                return False

            # Processar cada vaga
            for i, job_card in enumerate(job_cards):
                if not self.gui.is_running:  # Verificar se o bot foi pausado
                    return False

                try:
                    self.log(f"\nProcessando vaga {i+1} de {len(job_cards)}")
                    
                    # Rolar até o cartão da vaga
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", job_card)
                    time.sleep(1)
                    
                    # Tentar clicar no cartão da vaga
                    try:
                        # Primeiro tentar clicar diretamente
                        job_card.click()
                    except:
                        # Se falhar, tentar encontrar um elemento clicável dentro do cartão
                        clickable_elements = job_card.find_elements(By.TAG_NAME, "a")
                        if clickable_elements:
                            clickable_elements[0].click()
                        else:
                            # Tentar clicar via JavaScript
                            self.driver.execute_script("arguments[0].click();", job_card)
                    
                    time.sleep(3)  # Esperar a vaga carregar
                    
                    # Verificar se há botão de candidatura
                    apply_button = None
                    apply_button_selectors = [
                        (By.CLASS_NAME, "jobs-apply-button"),
                        (By.XPATH, "//button[contains(@class, 'jobs-apply-button')]"),
                        (By.XPATH, "//button[contains(., 'Candidatar')]"),
                        (By.XPATH, "//button[contains(., 'Easy Apply')]")
                    ]

                    for selector_type, selector in apply_button_selectors:
                        try:
                            apply_button = self.wait.until(
                                EC.element_to_be_clickable((selector_type, selector))
                            )
                            if apply_button:
                                self.log("Botão de candidatura encontrado!")
                                break
                        except:
                            continue

                    if not apply_button:
                        self.log("Não foi possível encontrar o botão de candidatura")
                        continue

                    # Clicar no botão de candidatura
                    apply_button.click()
                    time.sleep(2)

                    # Processar o formulário de candidatura
                    self.processar_formulario()

                except Exception as e:
                    self.log(f"Erro ao processar vaga {i+1}: {str(e)}")
                    continue

            return True

        except Exception as e:
            self.log(f"Erro ao candidatar às vagas: {str(e)}")
            return False
    
    def close(self):
        """Fechar o navegador"""
        self.driver.quit()

def main():
    gui = BotGUI()
    gui.run()

if __name__ == "__main__":
    main()
