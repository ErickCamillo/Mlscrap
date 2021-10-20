import requests
from json import dump
from sys import argv
from bs4 import BeautifulSoup

# Função de callback para filtrar valores em uma lista
def FilterValueCallback(lst):

	if int(lst['Preco'].replace('R$' , '').replace('.' , '')) <= maxvalueproduct: return True
	else: return False

# Analisa os dados para retornar o anuncio com menor preço
def FilterProductValue(content):

	lowervaluesproductlist = list(filter(FilterValueCallback , content))	
	return lowervaluesproductlist

# Retorna uma lista de dicionarios com dados de todos os produtos
def GetAllProduct(product_name):

	url = 'https://lista.mercadolivre.com.br/%s#D[A:%s]' %(product_name , product_name)
	header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0'}
	page = 1
	item = 1
	content = []

	s_req = requests.Session()
	s_req.headers.update(header)

	while(True):
		
		req = s_req.get(url)
		if req.status_code == 404:
			return req.status_code

		soup = BeautifulSoup(req.text , 'html.parser')
		
		# Obtem a lista de produtos completa de uma pagina
		product_list = soup.find_all('li' , class_='ui-search-layout__item')

		# Obtendo dados do anuncio
		for product in product_list:
			title = product.find('h2').text
			link = product.find('a')['href']
			product_value = product.find('span' , class_='price-tag-symbol').text
			product_value += product.find('span' , class_='price-tag-fraction').text
			data = {'Item' : item , 'Pagina' : page ,'Link da Pagina' : url , 'Titulo' : title , 'Link' : link , 'Preco' : product_value}
			content.append(data)
			item += 1

		# Obtendo a url da proxima pagina
		next_page = soup.find('a' , class_='andes-pagination__link ui-search-link' , title='Seguinte')
		if next_page == None:
			break

		url = next_page['href']
		page += 1
		item = 1

	return content

product_name = None
maxvalueproduct = None

if len(argv) > 1 and len(argv) == 3:
	product_name = argv[1]
	maxvalueproduct = int(argv[2])
elif len(argv) > 3:
	print('Use: %s [PRODUTO] [VALOR MAXIMO DO PRODUTO]' %(argv[0]))
	exit(1)
else:
	product_name = input('> Pesquisar por: ')
	maxvalueproduct = int(input('> Valor maximo do produto (Número inteiro): '))

if __name__ == '__main__':

	print('[INFO] Extraindo dados...')
	productList = GetAllProduct(product_name)
	if productList == 404:
		print('[%s] Nenhum produto foi encontrado procurando por: %s' %(productList , product_name))
		exit(0)

	print('[INFO] Filtrando dados...')
	LowerValueProductList =  FilterProductValue(productList)
	if not LowerValueProductList:
		print('Nenhum produto com o valor R$ %s ou menor, foi encontrado.' %(str(maxvalueproduct)))
	else:
		filename = product_name.replace(' ', '_') + '.json'
		print("[INFO] Criando arquivo com dados da busca: %s\n\tArquivo: %s" %(product_name, filename))
		file = open(filename , 'w' , encoding='utf-8-sig')
		dump({'Lista':LowerValueProductList}, file , indent=4 , ensure_ascii=False)
		file.close()
