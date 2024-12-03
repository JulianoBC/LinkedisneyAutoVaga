# LinkedIn Easy Apply Bot 🤖

Bot automatizado para candidaturas no LinkedIn usando Python, Selenium e interface gráfica Tkinter.

## 🌟 Funcionalidades

- **Login Automático**
  - Login seguro usando credenciais do arquivo .env
  - Detecção dinâmica de seletores
  - Tratamento de erros robusto

- **Busca de Vagas**
  - Busca por palavras-chave (ex: "Desenvolvedor")
  - Filtro automático para "Candidatura Simplificada"
  - Navegação entre páginas de resultados

- **Processo de Candidatura**
  - Clique automático em vagas
  - Preenchimento de formulários
  - Sistema de retry em caso de falhas
  - Log detalhado de ações

- **Interface Gráfica**
  - Botões de controle:
    * Iniciar
    * Pausar
    * Reiniciar
    * Próxima Ação
  - Lista de etapas clicável
  - Log em tempo real
  - Status atual do bot

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone [seu-repositorio]
cd VagasSimplificadasLinkedin
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo .env:
```env
LINKEDIN_EMAIL=seu_email@exemplo.com
LINKEDIN_PASSWORD=sua_senha
```

## 💻 Como Usar

1. Execute o bot:
```bash
python main.py
```

2. Use a interface para:
   - Iniciar o bot do começo
   - Clicar em uma etapa específica para começar dali
   - Pausar quando necessário
   - Pular para próxima ação se algo travar

## 🔄 Etapas do Bot

1. Inicializar navegador
2. Fazer login no LinkedIn
3. Navegar para página de vagas
4. Buscar por "Desenvolvedor"
5. Aplicar filtro de candidatura simplificada
6. Processar lista de vagas
7. Clicar em vaga
8. Verificar botão de candidatura
9. Preencher formulário
10. Enviar candidatura
11. Próxima vaga/página

## ⚙️ Configuração

### Requisitos
- Python 3.8+
- Chrome WebDriver
- Conta LinkedIn

### Dependências Principais
- selenium>=4.10.0
- python-dotenv>=1.0.0
- tkinter (vem com Python)

## 🛡️ Segurança

- Credenciais armazenadas em .env
- .gitignore configurado
- Sem armazenamento de dados sensíveis
- Proteção contra detecção de bot

## 🔍 Solução de Problemas

### Bot não clica na vaga
- Verifique se a página carregou completamente
- Use o botão "Próxima Ação"
- Reinicie o bot se necessário

### Erro de login
- Verifique suas credenciais no .env
- Certifique-se de não ter autenticação de dois fatores
- Tente fazer login manualmente primeiro

### Navegador fecha inesperadamente
- Verifique se o Chrome WebDriver está atualizado
- Reinicie o bot
- Verifique se não há outros processos do Chrome

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add: Amazing Feature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## ⚠️ Aviso Legal

Este bot é para fins educacionais. Use com responsabilidade e de acordo com os termos de serviço do LinkedIn.

## 📝 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## 📧 Contato

Seu Nome - [@seutwitter](https://twitter.com/seutwitter)

Link do Projeto: [https://github.com/seu-usuario/VagasSimplificadasLinkedin](https://github.com/seu-usuario/VagasSimplificadasLinkedin)
