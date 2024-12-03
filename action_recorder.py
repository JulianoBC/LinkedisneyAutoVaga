from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

class ActionRecorder:
    def __init__(self, driver):
        self.driver = driver
        self.actions_file = "linkedin_actions.json"
        self.recorded_actions = []
        self.setup_event_listeners()
        
    def setup_event_listeners(self):
        """Configurar listeners para capturar ações do usuário"""
        js_script = """
        console.log('Iniciando gravação de ações...');
        window.userActions = [];
        
        // Função para obter o seletor mais específico de um elemento
        function getBestSelector(element) {
            // Tentar ID primeiro
            if (element.id) {
                return {type: 'id', value: element.id};
            }
            
            // Tentar data-test-id ou outros atributos de teste
            const testId = element.getAttribute('data-test-id') || 
                          element.getAttribute('data-testid') || 
                          element.getAttribute('data-test');
            if (testId) {
                return {type: 'test-id', value: testId};
            }
            
            // Tentar aria-label
            const ariaLabel = element.getAttribute('aria-label');
            if (ariaLabel) {
                return {type: 'aria-label', value: ariaLabel};
            }
            
            // Tentar classe específica do LinkedIn
            const classList = Array.from(element.classList);
            const linkedinClass = classList.find(c => c.includes('artdeco-') || c.includes('ember-'));
            if (linkedinClass) {
                return {type: 'class', value: linkedinClass};
            }
            
            // Se nada específico encontrado, usar XPath
            return {type: 'xpath', value: getXPath(element)};
        }
        
        // Função para gerar XPath
        function getXPath(element) {
            if (element.id !== '')
                return `id("${element.id}")`;
            if (element === document.body)
                return element.tagName;

            var ix = 0;
            var siblings = element.parentNode.childNodes;
            for (var i = 0; i < siblings.length; i++) {
                var sibling = siblings[i];
                if (sibling === element)
                    return getXPath(element.parentNode) + '/' + element.tagName + '[' + (ix + 1) + ']';
                if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                    ix++;
            }
        }
        
        // Listener de cliques
        document.addEventListener('click', function(e) {
            const element = e.target;
            const selector = getBestSelector(element);
            const action = {
                type: 'click',
                timestamp: new Date().getTime(),
                selector: selector,
                tagName: element.tagName,
                text: element.textContent.trim(),
                url: window.location.href,
                position: {
                    x: e.clientX,
                    y: e.clientY
                }
            };
            window.userActions.push(action);
            console.log('Clique registrado:', action);
        }, true);
        
        // Listener de inputs
        document.addEventListener('input', function(e) {
            const element = e.target;
            const selector = getBestSelector(element);
            const action = {
                type: 'input',
                timestamp: new Date().getTime(),
                selector: selector,
                tagName: element.tagName,
                value: element.value,
                url: window.location.href
            };
            window.userActions.push(action);
            console.log('Input registrado:', action);
        }, true);
        
        // Listener de navegação
        let lastUrl = window.location.href;
        new MutationObserver(() => {
            const currentUrl = window.location.href;
            if (lastUrl !== currentUrl) {
                const action = {
                    type: 'navigation',
                    timestamp: new Date().getTime(),
                    from: lastUrl,
                    to: currentUrl
                };
                window.userActions.push(action);
                console.log('Navegação registrada:', action);
                lastUrl = currentUrl;
            }
        }).observe(document, {subtree: true, childList: true});
        
        console.log('Sistema de gravação iniciado com sucesso!');
        """
        try:
            self.driver.execute_script(js_script)
            print("Sistema de gravação iniciado!")
        except Exception as e:
            print(f"Erro ao iniciar gravação: {str(e)}")
    
    def save_actions(self):
        """Salvar ações gravadas"""
        try:
            actions = self.driver.execute_script("return window.userActions;")
            if actions:
                # Remover ações duplicadas
                seen = set()
                unique_actions = []
                for action in actions:
                    action_key = f"{action.get('timestamp')}_{action.get('type')}"
                    if action_key not in seen:
                        seen.add(action_key)
                        unique_actions.append(action)
                
                self.recorded_actions = unique_actions
                with open(self.actions_file, 'w') as f:
                    json.dump(self.recorded_actions, f, indent=4)
                print(f"Salvou {len(unique_actions)} ações únicas")
                return True
        except Exception as e:
            print(f"Erro ao salvar ações: {str(e)}")
            return False
    
    def start_recording(self):
        """Iniciar gravação contínua"""
        print("\n=== MODO DE GRAVAÇÃO ATIVADO ===")
        print("1. Suas ações estão sendo gravadas")
        print("2. As ações são salvas automaticamente a cada 5 segundos")
        print("3. Feche o navegador quando terminar\n")
        
        last_save = time.time()
        while True:
            try:
                # Verificar se navegador está aberto
                self.driver.current_url
                
                # Salvar a cada 5 segundos
                current_time = time.time()
                if current_time - last_save >= 5:
                    self.save_actions()
                    last_save = current_time
                
                time.sleep(1)
            except Exception as e:
                print("\nGravação finalizada")
                # Tentar salvar uma última vez
                self.save_actions()
                break
