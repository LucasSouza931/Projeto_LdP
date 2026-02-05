import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime

DB = "tarefas.json"


# -------- carregar / salvar --------
def carregar():
    if not os.path.exists(DB):
        return []
    with open(DB, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []


def salvar(tarefas):
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=2, ensure_ascii=False)


# -------- operações CRUD --------
def criar(tarefas, titulo):
    novo_id = max([t['id'] for t in tarefas], default=0) + 1
    data_criacao = datetime.now().strftime("%d/%m/%Y")
    
    tarefa = {
        "id": novo_id,
        "titulo": titulo,
        "status": "pendente",
        "criada_em": data_criacao
    }
    
    tarefas.append(tarefa)
    salvar(tarefas)
    return tarefa


def ler(tarefas, tarefa_id):
    return next((t for t in tarefas if t["id"] == tarefa_id), None)


def atualizar(tarefas, tarefa_id, novo_titulo=None):
    for tarefa in tarefas:
        if tarefa["id"] == tarefa_id:
            if novo_titulo:
                tarefa['titulo'] = novo_titulo
            salvar(tarefas)
            return tarefa
    return None


def concluir(tarefas, tarefa_id):
    for tarefa in tarefas:
        if tarefa["id"] == tarefa_id:
            tarefa['status'] = 'concluída'
            salvar(tarefas)
            return tarefa
    return None


def reabrir(tarefas, tarefa_id):
    for tarefa in tarefas:
        if tarefa["id"] == tarefa_id:
            tarefa['status'] = 'pendente'
            salvar(tarefas)
            return tarefa
    return None


def deletar(tarefas, tarefa_id):
    for tarefa in tarefas:
        if tarefa["id"] == tarefa_id:
            tarefas.remove(tarefa)
            salvar(tarefas)
            return True
    return False


# -------- Interface Gráfica --------
class ToDoListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 To-Do List")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        style.configure('TButton', font=('Arial', 10))
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), background='#f0f0f0', foreground='#2c3e50')
        
        self.tarefas = carregar()
        self.tarefa_selecionada = None
        
        self.criar_interface()
        self.atualizar_lista()
    
    def criar_interface(self):
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill='x', padx=20, pady=20)
        
        titulo = ttk.Label(header, text="📝 MINHAS TAREFAS", style='Title.TLabel')
        titulo.pack(side='left', fill='x', expand=True)
        
        # Frame de botões de ação
        frame_botoes = ttk.Frame(self.root)
        frame_botoes.pack(fill='x', padx=20, pady=10)
        
        btn_novo = ttk.Button(frame_botoes, text="➕ Nova Tarefa", command=self.nova_tarefa)
        btn_novo.pack(side='left', padx=5)
        
        btn_atualizar = ttk.Button(frame_botoes, text="🔄 Atualizar", command=self.atualizar_lista)
        btn_atualizar.pack(side='left', padx=5)
        
        btn_limpar = ttk.Button(frame_botoes, text="🗑️ Limpar Concluídas", command=self.limpar_concluidas)
        btn_limpar.pack(side='left', padx=5)
        
        # Frame de filtros
        frame_filtros = ttk.Frame(self.root)
        frame_filtros.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(frame_filtros, text="Filtrar:").pack(side='left', padx=5)
        
        self.var_filtro = tk.StringVar(value="todas")
        filtro_todas = ttk.Radiobutton(frame_filtros, text="Todas", variable=self.var_filtro, 
                                       value="todas", command=self.atualizar_lista)
        filtro_todas.pack(side='left', padx=5)
        
        filtro_pendentes = ttk.Radiobutton(frame_filtros, text="Pendentes", variable=self.var_filtro, 
                                           value="pendente", command=self.atualizar_lista)
        filtro_pendentes.pack(side='left', padx=5)
        
        filtro_concluidas = ttk.Radiobutton(frame_filtros, text="Concluídas", variable=self.var_filtro, 
                                            value="concluída", command=self.atualizar_lista)
        filtro_concluidas.pack(side='left', padx=5)
        
        # Frame da tabela
        frame_tabela = ttk.Frame(self.root)
        frame_tabela.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview
        self.tree = ttk.Treeview(frame_tabela, 
                                 columns=('ID', 'Tarefa', 'Status', 'Data'),
                                 height=15,
                                 yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Definir colunas
        self.tree.column('#0', width=0, stretch='no')
        self.tree.column('ID', anchor='center', width=40)
        self.tree.column('Tarefa', anchor='w', width=400)
        self.tree.column('Status', anchor='center', width=100)
        self.tree.column('Data', anchor='center', width=100)
        
        # Headers
        self.tree.heading('#0', text='')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Tarefa', text='Tarefa')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Data', text='Data')
        
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<Double-1>', self.editar_tarefa_duplo_clique)
        self.tree.bind('<Button-3>', self.menu_contexto)
        
        # Frame de ações
        frame_acoes = ttk.Frame(self.root)
        frame_acoes.pack(fill='x', padx=20, pady=10)
        
        btn_editar = ttk.Button(frame_acoes, text="✏️ Editar", command=self.editar_tarefa)
        btn_editar.pack(side='left', padx=5)
        
        btn_concluir = ttk.Button(frame_acoes, text="✓ Marcar Concluída", command=self.marcar_concluida)
        btn_concluir.pack(side='left', padx=5)
        
        btn_reabrir = ttk.Button(frame_acoes, text="↻ Reabrir", command=self.reabrir_tarefa)
        btn_reabrir.pack(side='left', padx=5)
        
        btn_deletar = ttk.Button(frame_acoes, text="🗑️ Deletar", command=self.deletar_tarefa)
        btn_deletar.pack(side='left', padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief='sunken')
        status_bar.pack(fill='x', side='bottom')
    
    def atualizar_lista(self):
        """Atualizar lista de tarefas na tela"""
        # Limpar tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Recarregar dados
        self.tarefas = carregar()
        
        # Obter filtro selecionado
        filtro = self.var_filtro.get()
        
        # Inserir tarefas
        for tarefa in self.tarefas:
            if filtro != "todas" and tarefa['status'] != filtro:
                continue
            
            status_emoji = "✓" if tarefa['status'] == 'concluída' else "○"
            self.tree.insert('', 'end', 
                           values=(tarefa['id'], 
                                  tarefa['titulo'], 
                                  f"{status_emoji} {tarefa['status'].capitalize()}",
                                  tarefa['criada_em']))
        
        # Atualizar status
        total = len(self.tarefas)
        concluidas = len([t for t in self.tarefas if t['status'] == 'concluída'])
        pendentes = total - concluidas
        
        self.status_var.set(f"Total: {total} | Pendentes: {pendentes} | Concluídas: {concluidas}")
    
    def nova_tarefa(self):
        """Abrir diálogo para criar nova tarefa"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nova Tarefa")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text="Título da tarefa:", font=('Arial', 10)).pack(pady=10)
        
        entry = ttk.Entry(dialog, width=40, font=('Arial', 10))
        entry.pack(pady=5, padx=20, fill='x')
        entry.focus()
        
        def salvar():
            titulo = entry.get().strip()
            if not titulo:
                messagebox.showwarning("Aviso", "Por favor, digite um título para a tarefa!")
                return
            
            criar(self.tarefas, titulo)
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Tarefa criada com sucesso!")
            dialog.destroy()
        
        frame_botoes = ttk.Frame(dialog)
        frame_botoes.pack(pady=20)
        
        ttk.Button(frame_botoes, text="Salvar", command=salvar).pack(side='left', padx=10)
        ttk.Button(frame_botoes, text="Cancelar", command=dialog.destroy).pack(side='left', padx=10)
    
    def editar_tarefa(self):
        """Editar tarefa selecionada"""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para editar!")
            return
        
        item = selecionado[0]
        valores = self.tree.item(item)['values']
        tarefa_id = valores[0]
        
        tarefa = ler(self.tarefas, tarefa_id)
        if not tarefa:
            messagebox.showerror("Erro", "Tarefa não encontrada!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Tarefa")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text="Novo título:", font=('Arial', 10)).pack(pady=10)
        
        entry = ttk.Entry(dialog, width=40, font=('Arial', 10))
        entry.insert(0, tarefa['titulo'])
        entry.pack(pady=5, padx=20, fill='x')
        entry.focus()
        
        def salvar():
            novo_titulo = entry.get().strip()
            if not novo_titulo:
                messagebox.showwarning("Aviso", "Por favor, digite um título!")
                return
            
            atualizar(self.tarefas, tarefa_id, novo_titulo)
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Tarefa atualizada!")
            dialog.destroy()
        
        frame_botoes = ttk.Frame(dialog)
        frame_botoes.pack(pady=20)
        
        ttk.Button(frame_botoes, text="Salvar", command=salvar).pack(side='left', padx=10)
        ttk.Button(frame_botoes, text="Cancelar", command=dialog.destroy).pack(side='left', padx=10)
    
    def editar_tarefa_duplo_clique(self, event):
        """Editar ao fazer duplo clique"""
        selecionado = self.tree.selection()
        if selecionado:
            self.editar_tarefa()
    
    def marcar_concluida(self):
        """Marcar tarefa como concluída"""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa!")
            return
        
        item = selecionado[0]
        valores = self.tree.item(item)['values']
        tarefa_id = valores[0]
        
        concluir(self.tarefas, tarefa_id)
        self.atualizar_lista()
        messagebox.showinfo("Sucesso", "Tarefa marcada como concluída!")
    
    def reabrir_tarefa(self):
        """Reabrir tarefa concluída"""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa!")
            return
        
        item = selecionado[0]
        valores = self.tree.item(item)['values']
        tarefa_id = valores[0]
        
        reabrir(self.tarefas, tarefa_id)
        self.atualizar_lista()
        messagebox.showinfo("Sucesso", "Tarefa reabertas!")
    
    def deletar_tarefa(self):
        """Deletar tarefa"""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para deletar!")
            return
        
        item = selecionado[0]
        valores = self.tree.item(item)['values']
        tarefa_id = valores[0]
        titulo = valores[1]
        
        if messagebox.askyesno("Confirmação", f"Tem certeza que deseja deletar:\n\n'{titulo}'?"):
            deletar(self.tarefas, tarefa_id)
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Tarefa deletada!")
    
    def limpar_concluidas(self):
        """Limpar todas as tarefas concluídas"""
        concluidas = [t for t in self.tarefas if t['status'] == 'concluída']
        
        if not concluidas:
            messagebox.showinfo("Aviso", "Nenhuma tarefa concluída para limpar!")
            return
        
        if messagebox.askyesno("Confirmação", f"Deletar {len(concluidas)} tarefa(s) concluída(s)?"):
            for tarefa in concluidas:
                deletar(self.tarefas, tarefa['id'])
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Tarefas concluídas removidas!")
    
    def menu_contexto(self, event):
        """Menu de contexto ao clicar com botão direito"""
        item = self.tree.selection()
        if not item:
            return
        
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="✏️ Editar", command=self.editar_tarefa)
        menu.add_command(label="✓ Concluir", command=self.marcar_concluida)
        menu.add_command(label="↻ Reabrir", command=self.reabrir_tarefa)
        menu.add_separator()
        menu.add_command(label="🗑️ Deletar", command=self.deletar_tarefa)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()


if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoListApp(root)
    root.mainloop()
