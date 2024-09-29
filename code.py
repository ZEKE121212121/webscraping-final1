from bs4 import BeautifulSoup
import requests

word = '20394i23904rwskfnsklefnse#@$^$%&%(&^*())'


# grabbing base URLS
home_link = 'https://books.toscrape.com/index.html'
url = 'https://books.toscrape.com/'
page_links = []

# developing all 50 url links from home Page
for i in range(1,51):
    path = 'catalogue/page-' + str(i) + '.html'
    page_links.append(url + path)

# initiating dictionary to store all books
books = {}

# function to get all information from books
def get_info(soup):

    table = soup.select('.product_page .table.table-striped')[0]
    title = soup.select('.col-sm-6.product_main')[0].find('h1').text
    number_available_element = soup.select('.instock.availability')[0]
    number_available = ''.join(filter(str.isdigit, str(number_available_element)))

    product_description_results = soup.select('#product_description + p')
    product_description = ''
    if len(product_description_results) > 0:
        product_description = product_description_results[0].text
    category = soup.select('.breadcrumb')[0].find_all('a')[2].text
    review_rating = soup.find('p', class_='star-rating')['class'][1]
    image_url = soup.select('.product_page .item.active')[0].find('img').attrs['src']
    image_url = current_link[0:27]+ image_url.replace('../../', '')
    for row in table.find_all('tr'):
      if row.find('th').text.upper() == 'UPC':
          upc_code = row.find('td').text
      elif row.find('th').text.upper() == 'PRICE (EXCL. TAX)':
          price_excl_tax = row.find('td').text.replace('Â','').replace('£', '')
      elif row.find('th').text.upper() == 'PRICE (INCL. TAX)':
          price_incl_tax = row.find('td').text.replace('Â','').replace('£', '')

# storing info in a dictionary
    book = {
        'title' : title,
        'Available Books' : number_available,
        'UPC Code' : upc_code,
        'Price Excluding Tax' : price_excl_tax,
        'Price Including Tax' : price_incl_tax,
        'Product Description' : product_description,
        'Category' : category,
        'Review Rating' : review_rating,
        'Image URL' : image_url,
        'Product Page URL' : current_link
    }

    return book


# loop through all 50 page links
for page_link in page_links:
    page_response = requests.get(page_link)
    soup  = BeautifulSoup(page_response.text, 'html.parser')
    page_response.close()
    book_links = soup.find_all('div',class_='image_container')

# loop through each product page and getting info
    for book_link in book_links:
        current_link = 'https://books.toscrape.com/catalogue/' + book_link.find('a').attrs['href']
        response = requests.get(current_link)
        book_info = get_info(BeautifulSoup(response.content.decode('utf-8','ignore'), 'html.parser'))
        response.close()
        book_category = book_info['Category']
        books_in_category = books.get(book_category, [])
        books_in_category.append(book_info)
        books[book_category] = books_in_category

# function to create csv title corresponding to category
def csv_name_gen(category_name):
    csv_name = ''
    csv_name = category_name.lower().replace(' ', '_')
    return 'categories/' + csv_name

# function to create jpg title corresponding to book title
def image_gen(title):
    img_name = ''
    for char in title:
        if char.isalnum():
            img_name += char

    return 'images/' + img_name

# column titles for csv files
columns = ['title','Available Books','UPC Code','Price Excluding Tax','Price Including Tax','Product Description','Category','Review Rating','Image URL','Product Page URL']

# loop through categories and book-lists
for category,booklist in books.items():
    file_name = csv_name_gen(category)

# intiating csv file and saved to categories files
    with open(file_name + '.csv', 'w', encoding="utf-8") as f:
        f.write('Title, Available Books, UPC, Price Excl Tax, Price Incl Tax, Product Description, Category, Review Rating, Image URL, Product Page URL \n')

# looping through books within book-list
        for book in booklist:

# adding column titles to csv files
            for column in columns:
                f.write('"')
                f.write(book[column])
                f.write('", ')
            f.write('\n')
            img_page_response = requests.get(book['Image URL'])
            img_page = img_page_response.content
            img_page_response.close()
            img_book_name = image_gen(book['title'])

# intiating jpg files and saved to images files
            with open(img_book_name + '.jpg', 'wb') as img:
                img.write(img_page)


