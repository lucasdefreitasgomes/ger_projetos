from flask import Flask, render_template, request, redirect
import sqlite3
from flask import jsonify

app = Flask(__name__)

# Função auxiliar para executar consultas no banco de dados


def execute_query(query, values=None):
    conn = sqlite3.connect('projeto.db')
    cursor = conn.cursor()

    if values:
        cursor.execute(query, values)
    else:
        cursor.execute(query)

    result = cursor.fetchall()

    conn.commit()
    conn.close()

    return result

# Rota inicial


@app.route('/')
def index():
    projetos = execute_query("SELECT * FROM projetos")
    return render_template('index.html', projetos=projetos)

# Rota para criar um novo projeto


@app.route('/projeto', methods=['GET', 'POST'])
def criar_projeto():
    if request.method == 'POST':
        nome = request.form['nome']
        execute_query("INSERT INTO projetos (nome) VALUES (?)", (nome,))
        return redirect('/')
    return render_template('criar_projeto.html')

# Rota para editar um projeto


@app.route('/projeto/<int:projeto_id>/editar', methods=['GET', 'POST'])
def editar_projeto(projeto_id):
    if request.method == 'POST':
        nome = request.form['nome']
        execute_query("UPDATE projetos SET nome=? WHERE id=?",
                      (nome, projeto_id))
        return redirect('/')

    projeto = execute_query("SELECT * FROM projetos WHERE id=?", (projeto_id,))
    return render_template('editar_projeto.html', projeto=projeto[0])

# Rota para excluir um projeto


@app.route('/projeto/<int:projeto_id>/excluir')
def excluir_projeto(projeto_id):
    execute_query("DELETE FROM projetos WHERE id=?", (projeto_id,))
    execute_query("DELETE FROM tarefas WHERE projeto_id=?", (projeto_id,))
    return redirect('/')

# Rota para exibir os detalhes de um projeto


@app.route('/projeto/<int:projeto_id>', methods=['GET', 'POST'])
def detalhes_projeto(projeto_id):
    if request.method == 'POST':
        nome = request.form['nome']
        prazo = request.form['prazo']
        projeto_id = int(request.form['projeto_id'])
        execute_query("INSERT INTO tarefas (nome, prazo, status, projeto_id) VALUES (?, ?, ?, ?)",
                      (nome, prazo, 'Pendente', projeto_id))
        return redirect(f'/projeto/{projeto_id}')

    projeto = execute_query("SELECT * FROM projetos WHERE id=?", (projeto_id,))
    tarefas = execute_query(
        "SELECT * FROM tarefas WHERE projeto_id=?", (projeto_id,))
    return render_template('detalhes_projeto.html', projeto=projeto[0], tarefas=tarefas, projeto_id=projeto_id)

# Rota para criar uma nova tarefa


@app.route('/projeto/<int:projeto_id>/tarefa', methods=['GET', 'POST'])
def criar_tarefa(projeto_id):
    if request.method == 'POST':
        nome = request.form['nome']
        prazo = request.form['prazo']
        execute_query("INSERT INTO tarefas (nome, prazo, status, projeto_id) VALUES (?, ?, ?, ?)",
                      (nome, prazo, 'Pendente', projeto_id))
        return redirect(f'/projeto/{projeto_id}')

    projeto = execute_query("SELECT * FROM projetos WHERE id=?", (projeto_id,))
    return render_template('criar_tarefa.html', projeto=projeto[0], projeto_id=projeto_id)

# Rota para editar uma tarefa


@app.route('/projeto/<int:projeto_id>/tarefa/<int:tarefa_id>/editar', methods=['GET', 'POST'])
def editar_tarefa(projeto_id, tarefa_id):
    if request.method == 'POST':
        nome = request.form['nome']
        prazo = request.form['prazo']
        status = request.form['status']
        execute_query("UPDATE tarefas SET nome=?, prazo=?, status=? WHERE id=?",
                      (nome, prazo, status, tarefa_id))
        return redirect(f'/projeto/{projeto_id}')

    projeto = execute_query("SELECT * FROM projetos WHERE id=?", (projeto_id,))
    tarefa = execute_query("SELECT * FROM tarefas WHERE id=?", (tarefa_id,))
    return render_template('editar_tarefa.html', projeto=projeto[0], tarefa=tarefa[0])

# Rota para excluir uma tarefa


@app.route('/projeto/<int:projeto_id>/tarefa/<int:tarefa_id>/excluir')
def excluir_tarefa(projeto_id, tarefa_id):
    execute_query("DELETE FROM tarefas WHERE id=?", (tarefa_id,))
    return redirect(f'/projeto/{projeto_id}')

# Rota para exibir todos os projetos


# Rota para exibir todos os projetos
@app.route('/all_projects')
def all_projects():
    projetos = execute_query("SELECT * FROM projetos")
    projetos_completos = []
    for projeto in projetos:
        projeto_id = projeto[0]
        tarefas = execute_query(
            "SELECT * FROM tarefas WHERE projeto_id=?", (projeto_id,))
        projetos_completos.append((projeto, tarefas))
    return render_template('all_projects.html', projetos=projetos_completos)


if __name__ == '__main__':
    app.run(debug=True)
