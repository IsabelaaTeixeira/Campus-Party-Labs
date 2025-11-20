# SecureBank - Workshop de SQL Injection

Sistema bancário vulnerável para demonstração educacional de SQL Injection.

---

## Instalação

### 1. Instale o Flask
```bash
pip install flask
```

### 2. Crie a estrutura de pastas
```
workshop-securebank/
├── app.py
├── README.md
└── templates/
    ├── login.html
    └── dashboard.html
```

### 3. Execute o servidor
```bash
python app.py
```

### 4. Acesse no navegador
```
http://127.0.0.1:5000
```

---
## Como Usar 

### **Cenário 1: Login Normal**
- Usuário: `eu`
- Senha: `mypass123`
- Resultado: Vê apenas sua conta (R$ 1.500,00)

### **Cenário 2: SQL Injection Attack**
- Usuário: `eu' OR '1'='1' --`
- Senha: `qualquer coisa`
- Resultado: Acesso ADMIN com todas as contas visíveis

### **Cenário 3: Roubar Dinheiro**
1. Após SQL Injection, vá em "Funções de Administrador"
2. **Transferir de:** Selecione `pessoaMuitoMuitoRica` (R$ 9.850.000,00)
3. **Transferir para:** Digite `admin` ou `eu`
4. **Valor:** Digite `1000000`
5. Clique em **Transferir**
6. Pronto! R$ 1.000.000 roubado com sucesso 

---

## Contas Disponíveis

| Usuário | Senha | Saldo |
|---------|-------|-------|
| admin | admin2024! | R$ 50.000,00 |
| eu | mypass123 | R$ 1.500,00 |
| pessoaMuitoMuitoRica | supersecret999 | R$ 9.850.000,00  |

---

## Código Vulnerável vs Seguro

### Vulnerável (não use!)
```python
query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
cursor.execute(query)
```

### Seguro (use sempre!)
```python
query = "SELECT * FROM users WHERE username=? AND password=?"
cursor.execute(query, (username, password))
```

---
