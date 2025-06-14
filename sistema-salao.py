import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


# Inicializa o banco de dados e garante que as tabelas existam
def init_db():
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()
    
    # Criação da tabela clientes com tratamento de erro
    try:
        cursor.execute("""
            CREATE TABLE clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL,
                idade INTEGER,
                email TEXT,
                telefone TEXT
            )
        """)
    except sqlite3.OperationalError:
        # Se a tabela já existe, verifica as colunas
        cursor.execute("PRAGMA table_info(clientes)")
        colunas = [info[1] for info in cursor.fetchall()]
        
        if 'idade' not in colunas:
            cursor.execute("ALTER TABLE clientes ADD COLUMN idade INTEGER")
        if 'email' not in colunas:
            cursor.execute("ALTER TABLE clientes ADD COLUMN email TEXT")
        if 'telefone' not in colunas:
            cursor.execute("ALTER TABLE clientes ADD COLUMN telefone TEXT")
    
    # Criação das outras tabelas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tempo INTEGER NOT NULL,
            preco REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            servico_id INTEGER,
            data TEXT,
            hora TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id),
            FOREIGN KEY(servico_id) REFERENCES servicos(id)
        )
    """)
    
    conn.commit()
    conn.close()

# Função para cadastrar cliente
def cadastrar_cliente():
    def salvar_cliente():
        nome = entry_nome.get().strip()
        cpf = entry_cpf.get().strip()
        idade = entry_idade.get().strip()
        email = entry_email.get().strip()
        telefone = entry_telefone.get().strip()

        if not nome or not cpf:
            messagebox.showerror("Erro", "Nome e CPF são obrigatórios.")
            return

        try:
            idade_int = int(idade) if idade else None
        except ValueError:
            messagebox.showerror("Erro", "Idade inválida.")
            return

        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nome, cpf, idade, email, telefone) VALUES (?, ?, ?, ?, ?)", 
                       (nome, cpf, idade_int, email, telefone))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
        janela.destroy()

    janela = tk.Toplevel(root)
    janela.title("Cadastrar Cliente")

    tk.Label(janela, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    entry_nome = tk.Entry(janela, width=30)
    entry_nome.grid(row=0, column=1)

    tk.Label(janela, text="CPF:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    entry_cpf = tk.Entry(janela, width=30)
    entry_cpf.grid(row=1, column=1)

    tk.Label(janela, text="Idade:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
    entry_idade = tk.Entry(janela, width=30)
    entry_idade.grid(row=2, column=1)

    tk.Label(janela, text="Email:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
    entry_email = tk.Entry(janela, width=30)
    entry_email.grid(row=3, column=1)

    tk.Label(janela, text="Telefone:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
    entry_telefone = tk.Entry(janela, width=30)
    entry_telefone.grid(row=4, column=1)

    tk.Button(janela, text="Salvar", command=salvar_cliente).grid(row=5, column=0, columnspan=2, pady=10)
    janela.grab_set()

# Função para listar clientes (atualizada para mostrar ID)
def listar_clientes():
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cpf, idade, email, telefone FROM clientes")
    rows = cursor.fetchall()
    conn.close()

    janela_lista = tk.Toplevel(root)
    janela_lista.title("Lista de Clientes")

    # Treeview
    colunas = ("ID", "Nome", "CPF", "Idade", "Email", "Telefone")
    tree = ttk.Treeview(janela_lista, columns=colunas, show="headings")

    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for row in rows:
        tree.insert("", "end", values=row)

    tree.pack(fill="both", expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(janela_lista, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

# Função para buscar clientes
def buscar_clientes():
    def buscar():
        termo = entry_busca.get().strip()
        if not termo:
            messagebox.showwarning("Atenção", "Digite um nome para buscar.")
            return

        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cpf, idade, email, telefone FROM clientes WHERE nome LIKE ?", ('%' + termo + '%',))
        resultados = cursor.fetchall()
        conn.close()

        # Limpa e insere resultados
        for item in tree.get_children():
            tree.delete(item)
        for row in resultados:
            tree.insert("", "end", values=row)

    janela_busca = tk.Toplevel(root)
    janela_busca.title("Buscar Cliente")

    tk.Label(janela_busca, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
    entry_busca = tk.Entry(janela_busca, width=30)
    entry_busca.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(janela_busca, text="Buscar", command=buscar).grid(row=0, column=2, padx=5, pady=5)

    colunas = ("ID", "Nome", "CPF", "Idade", "Email", "Telefone")
    tree = ttk.Treeview(janela_busca, columns=colunas, show="headings")

    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.grid(row=1, column=0, columnspan=3, padx=5, pady=10)

    scrollbar = ttk.Scrollbar(janela_busca, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=1, column=3, sticky='ns')

# Funções para editar e excluir clientes
def editar_cliente():
    def carregar_dados():
        cliente_id = entry_id.get().strip()
        if not cliente_id:
            messagebox.showerror("Erro", "Informe o ID do cliente")
            return

        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cursor.fetchone()
        conn.close()

        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado")
            return

        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, cliente[1])
        entry_cpf.delete(0, tk.END)
        entry_cpf.insert(0, cliente[2])
        entry_idade.delete(0, tk.END)
        entry_idade.insert(0, cliente[3] if cliente[3] else "")
        entry_email.delete(0, tk.END)
        entry_email.insert(0, cliente[4] if cliente[4] else "")
        entry_telefone.delete(0, tk.END)
        entry_telefone.insert(0, cliente[5] if cliente[5] else "")

    def salvar_edicao():
        cliente_id = entry_id.get().strip()
        nome = entry_nome.get().strip()
        cpf = entry_cpf.get().strip()
        idade = entry_idade.get().strip()
        email = entry_email.get().strip()
        telefone = entry_telefone.get().strip()

        if not nome or not cpf:
            messagebox.showerror("Erro", "Nome e CPF são obrigatórios")
            return

        try:
            idade_int = int(idade) if idade else None
        except ValueError:
            messagebox.showerror("Erro", "Idade deve ser um número")
            return

        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clientes 
            SET nome = ?, cpf = ?, idade = ?, email = ?, telefone = ?
            WHERE id = ?
        """, (nome, cpf, idade_int, email, telefone, cliente_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
        janela.destroy()

    janela = tk.Toplevel(root)
    janela.title("Editar Cliente")

    tk.Label(janela, text="ID do Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    entry_id = tk.Entry(janela, width=30)
    entry_id.grid(row=0, column=1)
    tk.Button(janela, text="Carregar", command=carregar_dados).grid(row=0, column=2, padx=5)

    tk.Label(janela, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    entry_nome = tk.Entry(janela, width=30)
    entry_nome.grid(row=1, column=1, columnspan=2)

    tk.Label(janela, text="CPF:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
    entry_cpf = tk.Entry(janela, width=30)
    entry_cpf.grid(row=2, column=1, columnspan=2)

    tk.Label(janela, text="Idade:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
    entry_idade = tk.Entry(janela, width=30)
    entry_idade.grid(row=3, column=1, columnspan=2)

    tk.Label(janela, text="Email:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
    entry_email = tk.Entry(janela, width=30)
    entry_email.grid(row=4, column=1, columnspan=2)

    tk.Label(janela, text="Telefone:").grid(row=5, column=0, padx=5, pady=5, sticky='e')
    entry_telefone = tk.Entry(janela, width=30)
    entry_telefone.grid(row=5, column=1, columnspan=2)

    tk.Button(janela, text="Salvar Edição", command=salvar_edicao).grid(row=6, column=0, columnspan=3, pady=10)
    janela.grab_set()

def excluir_cliente():
    def confirmar_exclusao():
        cliente_id = entry_id.get().strip()
        if not cliente_id:
            messagebox.showerror("Erro", "Informe o ID do cliente")
            return

        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este cliente?"):
            return

        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM agendamentos WHERE cliente_id = ?", (cliente_id,))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Erro", "Este cliente possui agendamentos e não pode ser excluído")
            conn.close()
            return

        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
        janela.destroy()

    janela = tk.Toplevel(root)
    janela.title("Excluir Cliente")

    tk.Label(janela, text="ID do Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    entry_id = tk.Entry(janela, width=30)
    entry_id.grid(row=0, column=1)

    tk.Button(janela, text="Excluir", command=confirmar_exclusao).grid(row=1, column=0, columnspan=2, pady=10)
    janela.grab_set()

# Funções para serviços
def cadastrar_servico():
    def salvar_servico():
        nome = entry_nome.get().strip()
        tempo = entry_tempo.get().strip()  # Alterado de descricao para tempo
        preco = entry_preco.get().strip()
        
        if not nome or not tempo:  # Tempo agora é obrigatório
            messagebox.showerror("Erro", "Nome e tempo são obrigatórios.")
            return
            
        try:
            tempo_int = int(tempo)  # Converte para inteiro (minutos)
            preco_float = float(preco) if preco else None
        except ValueError:
            messagebox.showerror("Erro", "Tempo deve ser um número inteiro e preço deve ser um valor numérico.")
            return

        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO servicos (nome, tempo, preco) VALUES (?, ?, ?)", 
                      (nome, tempo_int, preco_float))  # Alterado descricao para tempo
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Serviço cadastrado com sucesso!")
        janela.destroy()

    janela = tk.Toplevel(root)
    janela.title("Cadastrar Serviço")
    
    tk.Label(janela, text="Nome do Serviço:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
    entry_nome = tk.Entry(janela, width=30)
    entry_nome.grid(row=0, column=1)

    tk.Label(janela, text="Tempo (minutos):").grid(row=1, column=0, sticky='e', padx=5, pady=5)  # Alterado
    entry_tempo = tk.Entry(janela, width=30)  # Alterado de entry_descricao para entry_tempo
    entry_tempo.grid(row=1, column=1)

    tk.Label(janela, text="Preço (R$):").grid(row=2, column=0, sticky='e', padx=5, pady=5)
    entry_preco = tk.Entry(janela, width=30)
    entry_preco.grid(row=2, column=1)

    tk.Button(janela, text="Salvar", command=salvar_servico).grid(row=3, column=0, columnspan=2, pady=10)
    janela.grab_set()

def listar_servicos():
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, tempo, preco FROM servicos")  # Alterado descricao para tempo
    servicos = cursor.fetchall()
    conn.close()

    janela = tk.Toplevel(root)
    janela.title("Serviços Cadastrados")

    tree = ttk.Treeview(janela, columns=("ID", "Nome", "Tempo", "Preço"), show='headings')  # Alterado
    tree.heading("ID", text="ID")
    tree.heading("Nome", text="Nome")
    tree.heading("Tempo", text="Tempo (min)")  # Alterado
    tree.heading("Preço", text="Preço (R$)")
    
    tree.column("ID", width=50, anchor='center')
    tree.column("Nome", width=150)
    tree.column("Tempo", width=100, anchor='center')  # Alterado
    tree.column("Preço", width=80, anchor='center')
    
    tree.pack(fill='both', expand=True)

    for servico in servicos:
        tree.insert("", "end", values=servico)

def editar_servico():
    def carregar_dados():
        servico_id = entry_id.get().strip()
        if not servico_id:
            messagebox.showerror("Erro", "Informe o ID do serviço")
            return

        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servicos WHERE id = ?", (servico_id,))
        servico = cursor.fetchone()
        conn.close()

        if not servico:
            messagebox.showerror("Erro", "Serviço não encontrado")
            return

        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, servico[1])
        entry_tempo.delete(0, tk.END)
        entry_tempo.insert(0, str(servico[2]))
        entry_preco.delete(0, tk.END)
        entry_preco.insert(0, str(servico[3]) if servico[3] else "")

    def salvar_edicao():
        servico_id = entry_id.get().strip()
        nome = entry_nome.get().strip()
        tempo = entry_tempo.get().strip()
        preco = entry_preco.get().strip()

        if not nome or not tempo:
            messagebox.showerror("Erro", "Nome e tempo são obrigatórios")
            return

        try:
            tempo_int = int(tempo)
            preco_float = float(preco) if preco else None
        except ValueError:
            messagebox.showerror("Erro", "Tempo deve ser inteiro e preço deve ser numérico")
            return

        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE servicos 
            SET nome = ?, tempo = ?, preco = ?
            WHERE id = ?
        """, (nome, tempo_int, preco_float, servico_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Serviço atualizado com sucesso!")
        janela.destroy()

    janela = tk.Toplevel(root)
    janela.title("Editar Serviço")

    tk.Label(janela, text="ID do Serviço:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    entry_id = tk.Entry(janela, width=30)
    entry_id.grid(row=0, column=1)
    tk.Button(janela, text="Carregar", command=carregar_dados).grid(row=0, column=2, padx=5)

    tk.Label(janela, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    entry_nome = tk.Entry(janela, width=30)
    entry_nome.grid(row=1, column=1, columnspan=2)

    tk.Label(janela, text="Tempo (minutos):").grid(row=2, column=0, padx=5, pady=5, sticky='e')  # Corrigido
    entry_tempo = tk.Entry(janela, width=30)  # Corrigido
    entry_tempo.grid(row=2, column=1, columnspan=2)

    tk.Label(janela, text="Preço:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
    entry_preco = tk.Entry(janela, width=30)
    entry_preco.grid(row=3, column=1, columnspan=2)

    tk.Button(janela, text="Salvar Edição", command=salvar_edicao).grid(row=4, column=0, columnspan=3, pady=10)
    janela.grab_set()

def excluir_servico():
    def confirmar_exclusao():
        servico_id = entry_id.get().strip()
        if not servico_id:
            messagebox.showerror("Erro", "Informe o ID do serviço")
            return

        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este serviço?"):
            return

        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM agendamentos WHERE servico_id = ?", (servico_id,))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Erro", "Este serviço possui agendamentos e não pode ser excluído")
            conn.close()
            return

        cursor.execute("DELETE FROM servicos WHERE id = ?", (servico_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Serviço excluído com sucesso!")
        janela.destroy()

    janela = tk.Toplevel(root)
    janela.title("Excluir Serviço")

    tk.Label(janela, text="ID do Serviço:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    entry_id = tk.Entry(janela, width=30)
    entry_id.grid(row=0, column=1)

    tk.Button(janela, text="Excluir", command=confirmar_exclusao).grid(row=1, column=0, columnspan=2, pady=10)
    janela.grab_set()

# Funções para agendamentos
def agendar_servico():
    def salvar_agendamento():
        cliente_id = entry_cliente_id.get().strip()
        servico_id = entry_servico_id.get().strip()
        data = entry_data.get().strip()
        hora = entry_hora.get().strip()

        if not cliente_id or not servico_id or not data or not hora:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
            return

        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO agendamentos (cliente_id, servico_id, data, hora) VALUES (?, ?, ?, ?)",
                       (cliente_id, servico_id, data, hora))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Agendamento realizado com sucesso!")
        janela.destroy()

    janela = tk.Toplevel(root)
    janela.title("Agendar Serviço")

    tk.Label(janela, text="ID do Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    entry_cliente_id = tk.Entry(janela)
    entry_cliente_id.grid(row=0, column=1)

    tk.Label(janela, text="ID do Serviço:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    entry_servico_id = tk.Entry(janela)
    entry_servico_id.grid(row=1, column=1)

    tk.Label(janela, text="Data (dd/mm/aaaa):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
    entry_data = tk.Entry(janela)
    entry_data.grid(row=2, column=1)

    tk.Label(janela, text="Hora (hh:mm):").grid(row=3, column=0, padx=5, pady=5, sticky='e')
    entry_hora = tk.Entry(janela)
    entry_hora.grid(row=3, column=1)

    tk.Button(janela, text="Agendar", command=salvar_agendamento).grid(row=4, column=0, columnspan=2, pady=10)
    janela.grab_set()

def listar_agendamentos():
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, c.nome, s.nome || ' (' || s.tempo || ' min)', a.data, a.hora  # Alterado
        FROM agendamentos a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN servicos s ON a.servico_id = s.id
    """)
    agendamentos = cursor.fetchall()
    conn.close()

    janela = tk.Toplevel(root)
    janela.title("Agendamentos")

    tree = ttk.Treeview(janela, columns=("ID", "Cliente", "Serviço", "Data", "Hora"), show='headings')
    tree.heading("ID", text="ID")
    tree.heading("Cliente", text="Cliente")
    tree.heading("Serviço", text="Serviço")
    tree.heading("Data", text="Data")
    tree.heading("Hora", text="Hora")
    
    for col in ("ID", "Cliente", "Serviço", "Data", "Hora"):
        tree.column(col, width=100, anchor='center')

    tree.pack(fill='both', expand=True)

    for row in agendamentos:
        tree.insert("", "end", values=row)

# --------------- INTERFACE PRINCIPAL -----------------
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    root.title("Sistema de Cadastro - Salão de Beleza")

    # Frame principal para organização
    main_frame = tk.Frame(root)
    main_frame.pack(padx=20, pady=20)

    # Seção Clientes
    tk.Label(main_frame, text="--- Clientes ---", font=('Arial', 10, 'bold')).grid(row=0, column=0, pady=5)
    tk.Button(main_frame, text="Cadastrar Cliente", width=25, command=cadastrar_cliente).grid(row=1, column=0, pady=3)
    tk.Button(main_frame, text="Listar Clientes", width=25, command=listar_clientes).grid(row=2, column=0, pady=3)
    tk.Button(main_frame, text="Buscar Clientes", width=25, command=buscar_clientes).grid(row=3, column=0, pady=3)
    tk.Button(main_frame, text="Editar Cliente", width=25, command=editar_cliente).grid(row=4, column=0, pady=3)
    tk.Button(main_frame, text="Excluir Cliente", width=25, command=excluir_cliente).grid(row=5, column=0, pady=3)

    # Seção Serviços
    tk.Label(main_frame, text="--- Serviços ---", font=('Arial', 10, 'bold')).grid(row=0, column=1, pady=5)
    tk.Button(main_frame, text="Cadastrar Serviço", width=25, command=cadastrar_servico).grid(row=1, column=1, pady=3)
    tk.Button(main_frame, text="Listar Serviços", width=25, command=listar_servicos).grid(row=2, column=1, pady=3)
    tk.Button(main_frame, text="Editar Serviço", width=25, command=editar_servico).grid(row=3, column=1, pady=3)
    tk.Button(main_frame, text="Excluir Serviço", width=25, command=excluir_servico).grid(row=4, column=1, pady=3)

    # Seção Agendamentos
    tk.Label(main_frame, text="--- Agendamentos ---", font=('Arial', 10, 'bold')).grid(row=0, column=2, pady=5)
    tk.Button(main_frame, text="Agendar Serviço", width=25, command=agendar_servico).grid(row=1, column=2, pady=3)
    tk.Button(main_frame, text="Listar Agendamentos", width=25, command=listar_agendamentos).grid(row=2, column=2, pady=3)

    root.mainloop()