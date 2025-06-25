import time
import pandas as pd 
import collections
import tkinter as tk
from tkinter import ttk, scrolledtext
from io import StringIO
import sys


class filme: 
    def __init__(self, movieid, titulo, generos, ano):
        self.movieid = movieid
        self.titulo = titulo
        self.generos = generos
        self.ano = ano
        self.ratings = 0
        self.somaratings = 0 
    
    def __str__(self):
        return f"{self.movieid} - {self.titulo} ({self.ano})\nGêneros: {self.generos}\nAvaliações: {self.ratings} | Soma: {self.somaratings}"

class tags:

    def __init__(self ,tag):
        self.tag = tag
        self.moviesids = []
    
    def insere_movie (self, movieid):

        if movieid not in self.moviesids:
            self.moviesids.append(movieid)

    def __str__(self):
        return f"{self.tag} - {self.moviesids}"

class usuario:
    def __init__(self, userid):
        self.userid = userid
        self.avaliacoes = []

    def insere_avaliacao(self, movieid, rating):
        self.avaliacoes.append((movieid, rating))

    def __str__(self):
        return f"{self.userid} - {self.avaliacoes}"
    

class nodo:
    def __init__(self, key, valor):
        self.key = key
        self.valor = valor
        self.next = None

class hashtable_string:                     #tipo de hash para lidar com string ao inves de inteiros
        
    def __init__(self,tam):
        self.tam = tam                      #tamanho da hash
        self.size = 0                           #qnt de elementos atuais
        self.table = [None] * tam
    

    def hashfunc_tags (self, tag):
        hash_val = 0
        for c in tag.lower():
            hash_val = (hash_val * 31 + ord(c)) % self.tam
        return hash_val


    def insert(self, key, value):
        key = key.strip().lower().replace("-","").replace(" ","")

        index = self.hashfunc_tags(key)
    
        if self.table[index] is not None:
            atual = self.table[index]
            while atual:
                if atual.key == key.lower():
                    return
                atual = atual.next
    

        novo_nodo = nodo(key.lower(), value)
        novo_nodo.next = self.table[index]
        self.table[index] = novo_nodo


    def search(self, key):
        key = key.strip().lower().replace("-","").replace(" ","")
        index = self.hashfunc_tags(key)

        atual = self.table[index]
        while atual:
            if atual.key == key.lower():
                return atual.valor
            atual = atual.next   
        
        return None
    

class hashtable:
    def __init__(self,tam):
        self.tam = tam                      #tamanho da hash
        self.size = 0                           #qnt de elementos atuais
        self.table = [None] * tam                   #lista caso colisao


    def hash_func(self, key):
        return key % self.tam
    
    
    def insert (self, key, valor):
        index = self.hash_func(key)
        novo_nodo = nodo(key, valor)

        if self.table[index] is not None:
            atual = self.table[index]
            while atual:
                if atual.key == key:
                    return
                atual = atual.next
        novo_nodo.next = self.table[index]
        self.table[index] = novo_nodo
        self.size += 1

    def search(self, key):
        index = self.hash_func(key)

        atual = self.table[index]
        while atual:
            if atual.key == key:
                return atual.valor
            atual = atual.next   
        
        return None
            
    def insert_rating(self, key, rating):
        index = self.hash_func(key)

        atual = self.table[index]
        while atual:
            if atual.key == key:
                atual.valor.ratings += 1
                atual.valor.somaratings += rating
                return
            atual = atual.next
        
        return None



class trie_node:
    def __init__(self):
        self.filho = [None] * 26
        self.fim_id = None
    
class trie_tree:
    def __init__(self):
        self.root = trie_node()

    def insere_arvore(self, movie_id, nome):
        atual = self.root
        for c in nome.lower():
            if 'a' <= c <= 'z':
                index = ord(c) - ord('a')
                if atual.filho[index] is None:

                    atual.filho[index] = trie_node()

                atual = atual.filho[index]

        atual.fim_id = movie_id


    def buscar_prefix(self, prefixo):
        prefixo = prefixo.lower()
        if not any('a' <= c <= 'z' for c in prefixo):
            return []
        
        atual = self.root #acessa nó raiz
        ids_encontrados = [] #cria lista para ids encontrados

        for c in prefixo.lower(): #for para analisar cada caractere

            if 'a' <= c <= 'z':
                index = ord(c) - ord('a')

                if atual.filho[index] is None:
                    return []
                
                atual = atual.filho[index]

       
        fila = collections.deque([atual]) 

        while fila:
            nodo_atual = fila.popleft()                               #pega o próximo nó da fila

            if nodo_atual.fim_id:
                ids_encontrados.append(nodo_atual.fim_id)

            for filho in nodo_atual.filho:
                if filho is not None:
                    fila.append(filho)
        
        return ids_encontrados

def mergesort(lista, key=lambda x: x):
    if len(lista) > 1:
        mid = len(lista) // 2
        lefthalf = lista[:mid]
        righthalf = lista[mid:]

        mergesort(lefthalf, key)
        mergesort(righthalf, key)

        i = j = k = 0

        while i < len(lefthalf) and j < len(righthalf):
            if key(lefthalf[i]) < key(righthalf[j]):
                lista[k] = lefthalf[i]
                i += 1
            else:
                lista[k] = righthalf[j]
                j += 1
            k += 1

        while i < len(lefthalf):
            lista[k] = lefthalf[i]
            i += 1
            k += 1

        while j < len(righthalf):
            lista[k] = righthalf[j]
            j += 1
            k += 1
            

def organiza_e_printa_prefix(trie, prefixo, hash_filmes):
    ids_prefix = trie.buscar_prefix(prefixo)
    filmes = []
    if not ids_prefix:
        print("Nenhum filme contém esse prefixo.")
        return
    else:
        for movie_id in ids_prefix:
            filme_prefix = hash_filmes.search(movie_id)
            if filme_prefix and filme_prefix.ratings > 0:
                media = filme_prefix.somaratings / filme_prefix.ratings
                filmes.append((filme_prefix.movieid, filme_prefix.titulo,filme_prefix.generos,filme_prefix.ano, media, filme_prefix.ratings))


        mergesort(filmes, key=lambda x: x[4])
        filmes.reverse()
        print(f"{'movieID'}\t {'Título':30}\t {'Gêneros':40}\t {'Ano':4}\t {'Média':13}\t {'Count'}")
        print("-" * 110)
        for movie_id, titulo, generos, ano, media, ratings in filmes:
            print(f"{movie_id}\t {titulo[:30]:30}\t {generos[:40]:40}\t {ano:4}\t {media:8.6f}\t {ratings:10}")

def filme_por_usuario(usuarioId, hash_usuario, hash_filmes):
    usuario = hashusuario.search(usuarioId)
    if usuario is None:
        print(f"Usuário {usuarioId} não encontrado.")
        return
    
    filmes_por_usuario = []      #reorganizaçao para funcionar com o merge

    for movie_id, rating in usuario.avaliacoes:
        filme = hash_filmes.search(movie_id)
        if filme:
            media = filme.somaratings / filme.ratings
            filmes_por_usuario.append((rating, media, filme.movieid, filme.titulo, filme.generos, filme.ano, filme.ratings))

    mergesort(filmes_por_usuario, key=lambda x: (x[0],x[1]))
    filmes_por_usuario.reverse()

    print(f"{'movieID'}\t {'Título':20}\t {'Gêneros':40}\t {'Ano':4}\t {'Média':12}\t {'Ratings'}\t {'Rating Usuário'}")
    print("-" * 118)
    for filme in filmes_por_usuario[:20]:
        rating_usuario, media, movie_id, titulo, generos, ano, ratings = filme
        print(f"{movie_id}\t {titulo[:20]:20}\t {generos[:40]:40}\t {ano:4}\t {media:8.6f}\t {ratings:10}\t {rating_usuario:10.2f}")
    
def melhor_por_genero(tam, hash, genero):
    genero = genero.lower()
    filmes_por_genre = []
    for i in range(hash.tam):
        atual = hash.table[i]
        while atual:
            filme = atual.valor

            if genero in filme.generos.lower().split('|') and filme.ratings >= 1000:
                media = filme.somaratings / filme.ratings
                filmes_por_genre.append((filme.movieid, filme.titulo, filme.generos, filme.ano, media, filme.ratings))
            atual = atual.next

    if not filmes_por_genre:
        print(f"Nenhum filme encontrado para o gênero {genero}")
        return
    if tam > len(filmes_por_genre):
        tam = len(filmes_por_genre)
        print(f"A quantidade solicitada é maior que a quantidade encontrada. Exibiindo {tam} filmes")

    mergesort(filmes_por_genre, key= lambda x: x[4])
    filmes_por_genre.reverse()
    print(f"{'movieId'}\t {'Título':20}\t {'Gêneros':40}\t {'Ano':4}\t {'Média':13}\t {'Count'}")
    print("-" * 100)
    for filme in filmes_por_genre[:tam]:
        movie_id,titulo, generos, ano, media, ratings = filme
        print(f"{movie_id}\t {titulo[:20]:20}\t {generos[:40]:40}\t {ano:4}\t {media:7.6f}\t {ratings:10}")


def intersec_tags(tags_in,hash_tags,hash_filmes):
    tag_list = [tag.strip().lower().replace("-","").replace(" ","") for tag in tags_in.split(',') if tag.strip()]
    if not tag_list:
        print("Nenhuma tag de entrada")
        return
    
    for tag_text in tag_list:
        tag_obj = hash_tags.search(tag_text)
        if tag_obj is None:
            print(f"Tag '{tag_text}' não encontrada.")


    intersec = None

    for tag in tag_list:
        tag = hash_tags.search(tag)
        if tag is None:
            print(f"'{tag}' não encontrada.")
            continue
        ids = set(tag.moviesids)
        if intersec is None:
            intersec = ids
        else:
            intersec = intersec.intersection(ids)
        if not intersec:
            print("Nenhum filme contém todas as tags de entrada.")
            return 
    
    total = []
        
    for movie_id in intersec:
        filme = hash_filmes.search(movie_id)
        if filme and filme.ratings > 0:
            media = filme.somaratings / filme.ratings
            total.append((filme.movieid, filme.titulo, filme.generos, filme.ano, media, filme.ratings))

    if total == []:
        print("Nenhum filme encontrado com as tags fornecidas.")
        return
    
    mergesort(total, key=lambda x: x[4])
    total.reverse()

    print(f"{'movieId'}\t {'Título':20}\t {'Gêneros':40}\t {'Ano':4}\t {'Média':13}\t {'Count'}")
    print("-" * 100) 
    
    for filme in total:
        movie_id, titulo, generos, ano, media, ratings = filme
        print(f"{movie_id}\t {titulo[:20]:20}\t {generos[:40]:40}\t {ano:4}\t {media:7.6f}\t {ratings:10}")


hash = hashtable(9999973)
hashusuario = hashtable(5003)
hashtags = hashtable_string(50021)
titulos = trie_tree()

df_movies = pd.read_csv("movies.csv", encoding="utf-8")             #ler moviesid
start_time = time.time()
for row in df_movies.itertuples(index=False):
    movie_id = int(row.movieId)
    movie_title = row.title
    movie_genres = row.genres
    movie_year = int(row.year)

    novo_filme = filme(movie_id, movie_title,movie_genres,movie_year)
    hash.insert(movie_id, novo_filme)
    titulos.insere_arvore(movie_id, movie_title)


df_ratings = pd.read_csv("ratings.csv", encoding="utf-8")           #lerratings

for row in df_ratings.itertuples(index=False):
    user_id = int(row.userId)
    movie_id = int(row.movieId)
    rating = float(row.rating)

    hash.insert_rating (movie_id, rating)
    usuario_existente = hashusuario.search(user_id)

    if usuario_existente is None:
        usuario_novo = usuario(user_id)
        hashusuario.insert(user_id, usuario_novo)
        usuario_novo.insere_avaliacao(movie_id, rating)

    else:
        usuario_existente.insere_avaliacao(movie_id, rating)
    
    
df_tags = pd.read_csv("tags.csv", encoding="utf-8")

for row in df_tags.itertuples(index=False):
    movie_id = int(row.movieId)
    tag_text = str(row.tag).strip().lower().replace("-","")  # Normaliza a tag para minúsculas e remove espaços

    tag_obj = hashtags.search(tag_text)

    if tag_obj is None:
        tag_nova = tags(tag_text)
        tag_nova.insere_movie(movie_id)
        hashtags.insert(tag_text, tag_nova)
    
    else:
        tag_obj.insere_movie(movie_id)

end_time = time.time()
tempo_total = end_time-start_time
print (f"Tempo para geração das tabelas = {tempo_total:.4f}")


def iniciar_interface():


    root = tk.Tk()
    root.title("Sistema de Busca de Filmes")
    root.geometry("1200x700")  # ajusta tamanho da janela

    tabControl = ttk.Notebook(root)

    tabs = {}
    nomes = ["Buscar por Prefixo", "Buscar por Usuário", "Melhores por Gênero", "Intersecção de Tags"]
    for nome in nomes:
        tab = ttk.Frame(tabControl)
        tabControl.add(tab, text=nome)
        tabs[nome] = tab
    tabControl.pack(expand=1, fill="both")

    def limpar_tela(event):
        ajuste_saida.delete("1.0", tk.END)

    tabControl.bind("<<NotebookTabChanged>>", limpar_tela) #limpa a tela após troca de pesquisa
    ajuste_saida = scrolledtext.ScrolledText(root, width=180, height=25, font=("Courier", 10))
    ajuste_saida.pack(padx=10, pady=10)

    def executar(func):
        ajuste_saida.delete("1.0", tk.END)
        buffer = StringIO()
        sys.stdout = buffer
        try:
            func()
        except Exception as e:
            print(f"Erro: {e}")
        sys.stdout = sys.__stdout__
        ajuste_saida.insert(tk.END, buffer.getvalue())

    # Melhor por gênero
    genero_label = tk.Label(tabs["Melhores por Gênero"], text="Gênero:")
    genero_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
    genero_entry = tk.Entry(tabs["Melhores por Gênero"])
    genero_entry.grid(row=0, column=1, padx=5)

    quantidade_label = tk.Label(tabs["Melhores por Gênero"], text="Quantidade:")
    quantidade_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
    quantidade_entry = tk.Entry(tabs["Melhores por Gênero"])
    quantidade_entry.grid(row=1, column=1, padx=5)

    botao_genero = tk.Button(tabs["Melhores por Gênero"], text="Buscar", command=lambda: executar(
        lambda: melhor_por_genero(int(quantidade_entry.get()), hash, genero_entry.get())))
    botao_genero.grid(row=2, column=0, columnspan=2, pady=10)

    # Buscar por prefixo
    prefixo_label = tk.Label(tabs["Buscar por Prefixo"], text="Prefixo:")
    prefixo_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
    prefixo_entry = tk.Entry(tabs["Buscar por Prefixo"])
    prefixo_entry.grid(row=0, column=1, padx=5)

    botao_prefixo = tk.Button(tabs["Buscar por Prefixo"], text = "Buscar", command = lambda: executar
         (lambda: organiza_e_printa_prefix(titulos,prefixo_entry.get(), hash)))
    botao_prefixo.grid(row = 1, column = 0, columnspan = 2, pady = 10)

    # Buscar por usuário
    usuario_label = tk.Label(tabs["Buscar por Usuário"], text = "Usuário ID:")
    usuario_label.grid(row = 0, column = 0, sticky = "e", padx = 5, pady = 5)
    usuario_entry = tk.Entry(tabs["Buscar por Usuário"])
    usuario_entry.grid(row = 0, column = 1, padx = 5)

    botao_usuario = tk.Button(tabs["Buscar por Usuário"], text = "Buscar", command = lambda: executar(
        lambda: filme_por_usuario(int(usuario_entry.get()), hashusuario, hash)))
    botao_usuario.grid(row = 1, column = 0, columnspan = 2,pady = 10)
    
    # Intersecção de Tags
    intersec_label = tk.Label(tabs["Intersecção de Tags"], text = "Tags (separe por vírgula):")
    intersec_label.grid(row = 0, column = 0, sticky = "e", padx = 5, pady = 5)
    intersec_entry = tk.Entry(tabs["Intersecção de Tags"])
    intersec_entry.grid(row = 0, column = 1, padx = 10)

    botao_intersec = tk.Button(tabs["Intersecção de Tags"], text = "Buscar", command = lambda: executar(
        lambda: intersec_tags(intersec_entry.get(), hashtags, hash)))
    botao_intersec.grid(row = 1, column = 0, columnspan = 2, pady = 10)

    #saida
    botao_sair = tk.Button(root, text = "Sair", command = root.destroy)
    botao_sair.pack(pady = 10)
    
    root.mainloop()


iniciar_interface()