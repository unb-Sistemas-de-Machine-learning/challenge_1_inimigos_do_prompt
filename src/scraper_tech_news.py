import os
import time
import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

# Headers para simular um navegador real
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'lxml')
        else:
            print(f"Erro ao acessar {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Erro de conexão ao acessar {url}: {e}")
    return None

def scrape_manual_do_usuario_article(url):
    soup = get_soup(url)
    if not soup:
        return None
    
    content_div = soup.find('div', class_='e-content')
    if not content_div:
        content_div = soup.find('div', class_='entry-content')
        
    if not content_div:
        return None
    
    paragraphs = []
    # Remover scripts, tags de anúncios, etc.
    for tag in content_div.find_all(['script', 'style', 'ins', 'iframe']):
        tag.decompose()
        
    for p in content_div.find_all('p'):
        text = p.get_text().strip()
        if text:
            paragraphs.append(text)
            
    return "\n".join(paragraphs)

def scrape_manual_do_usuario_page(page_num):
    url = f"https://manualdousuario.net/page/{page_num}/" if page_num > 1 else "https://manualdousuario.net/"
    print(f"Scrapeando Manual do Usuário - Página {page_num}...")
    soup = get_soup(url)
    if not soup:
        return []
    
    articles = []
    # No Manual do Usuário, os títulos ficam em h2 com a classe p-name
    h2_tags = soup.find_all('h2', class_='p-name')
    for h2 in h2_tags:
        a_tag = h2.find('a')
        if a_tag:
            title = a_tag.get_text().strip()
            link = a_tag['href']
            articles.append({
                'source': 'manual_do_usuario',
                'title': title,
                'url': link,
                'publish_date': None  # Data pode ser extraída na página de detalhe se necessário
            })
    return articles

def scrape_g1_article(url):
    soup = get_soup(url)
    if not soup:
        return None
    
    paragraphs = []
    # G1 usa a classe 'content-text__container' para seus parágrafos de conteúdo
    p_tags = soup.find_all('p', class_='content-text__container')
    for p in p_tags:
        text = p.get_text().strip()
        if text:
            paragraphs.append(text)
            
    if not paragraphs:
        # Tenta pegar parágrafos normais se a classe falhar
        body_div = soup.find('div', class_='mc-column')
        if body_div:
            for p in body_div.find_all('p'):
                text = p.get_text().strip()
                if text:
                    paragraphs.append(text)
                    
    return "\n".join(paragraphs)

def scrape_g1_page(page_num):
    # O feed de paginação do G1 segue o formato abaixo
    url = f"https://g1.globo.com/tecnologia/index/feed/pagina-{page_num}.ghtml"
    print(f"Scrapeando G1 Tecnologia - Página {page_num}...")
    soup = get_soup(url)
    if not soup:
        return []
    
    articles = []
    # No G1, os links possuem a classe feed-post-link
    links = soup.find_all('a', class_='feed-post-link')
    for link in links:
        title = link.get_text().strip()
        url_dest = link['href']
        
        # Encontra a data relativa ou datetime se houver
        publish_date = None
        parent_post = link.find_parent('div', class_='feed-post-body')
        if parent_post:
            date_tag = parent_post.find('span', class_='feed-post-datetime')
            if date_tag:
                publish_date = date_tag.get_text().strip()
                
        articles.append({
            'source': 'g1',
            'title': title,
            'url': url_dest,
            'publish_date': publish_date
        })
    return articles

def main():
    parser = argparse.ArgumentParser(description="Scraper de notícias de tecnologia em português")
    parser.add_argument("--pages", type=int, default=3, help="Número de páginas para raspar de cada fonte (padrão: 3)")
    parser.add_argument("--delay", type=float, default=1.0, help="Tempo de espera entre requisições (padrão: 1.0)")
    args = parser.parse_args()
    
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    
    all_articles = []
    
    # 1. Scraping Manual do Usuário
    print(f"Iniciando scraping do Manual do Usuário ({args.pages} páginas)...")
    for p in range(1, args.pages + 1):
        page_arts = scrape_manual_do_usuario_page(p)
        if not page_arts:
            break
        all_articles.extend(page_arts)
        time.sleep(args.delay)
        
    # 2. Scraping G1 Tecnologia
    print(f"Iniciando scraping do G1 Tecnologia ({args.pages} páginas)...")
    for p in range(1, args.pages + 1):
        page_arts = scrape_g1_page(p)
        if not page_arts:
            break
        all_articles.extend(page_arts)
        time.sleep(args.delay)
        
    print(f"Total de links de tecnologia coletados: {len(all_articles)}")
    
    # 3. Coleta do texto dos artigos
    detailed_articles = []
    for art in tqdm(all_articles, desc="Coletando corpo das notícias"):
        url = art['url']
        if art['source'] == 'manual_do_usuario':
            text = scrape_manual_do_usuario_article(url)
        elif art['source'] == 'g1':
            text = scrape_g1_article(url)
        else:
            text = None
            
        if text:
            art['text'] = text
            detailed_articles.append(art)
            
        time.sleep(args.delay)
        
    df = pd.DataFrame(detailed_articles)
    
    # Salvar resultados
    output_path = os.path.join(data_dir, "tech_news.csv")
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Scraping finalizado! Dados de tecnologia salvos em: {output_path}")
    print(f"Total de registros de tecnologia salvos: {len(df)}")

if __name__ == "__main__":
    main()
