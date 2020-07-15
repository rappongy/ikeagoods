import json

import scrapy


class GoodsSpider(scrapy.Spider):
    name = 'goods'
    allowed_domains = [
        'www.ikea.com',
        'sik.search.blue.cdtapps.com',
    ]
    start_urls = ['https://www.ikea.com/ru/ru/cat/tovary-products/']

    # for dev purpose
    # def start_requests(self):
    #     yield scrapy.Request('https://www.ikea.com/ru/ru/cat/tovary-dlya-sobak-39570/', callback=self.parse_category)

    def parse(self, response):
        categories = {
            category.css('::attr(href)').get(): category.css('span::text').get()
            for category in response.css('li>a.vn-link.vn-nav__link')
        }

        yield from response.follow_all(categories.keys(), callback=self.parse_category)

    def parse_category(self, response):
        goods_on_page = len(response.css('.plp-product-list__products .range-revamp-product-compact'))

        category_data = json.loads(response.css('.js-product-list::attr(data-category)').get())
        # pages_data['pagination']
        goods_all = category_data['totalCount']

        self.logger.info(f'Category - {category_data["id"]}')
        self.logger.info(f'Goods all - {goods_all}, on this page - {goods_on_page}')

        category_goods_url = f'https://sik.search.blue.cdtapps.com/ru/ru/product-list-page?category={category_data["id"]}&size={goods_all}'
        yield response.follow(category_goods_url, callback=self.parse_category_json)

        # for good in response.css('.plp-product-list__products .range-revamp-product-compact'):
        #     good_id = good.css('::attr(data-product-number)').get()
        #
        #     assert good_id == good.css('::attr(data-ref-id)').get()
        #     assert good.css('::attr(data-currency)').get() == 'RUB'
        #
        #     good_dir = {
        #         'name': good.css('::attr(data-product-name)').get(),
        #         'price': good.css('::attr(data-price)').get(),
        #         'link': good.css('a[aria-label]::attr(href)').get(),
        #         'id': good_id,
        #         'desc': good.css('.range-revamp-header-section__description::text').get(),
        #         'desc_list': good.css('.range-revamp-header-section__description-text::text').getall(),
        #         'price_text': good.css('.range-revamp-price::text').get(),
        #         'is_yellow_price': bool(good.css('.range-revamp-price--highlight').get()),
        #     }
        #
        #     yield good_dir

    def parse_category_json(self, response):
        products_data = json.loads(response.body)["productListPage"]
        category_data = products_data["category"]

        self.logger.info(f'Category - {category_data}')
        self.logger.info(f'Products - {products_data["productCount"]}')

        for product in products_data["productWindow"]:
            assert product['currencyCode'] == 'RUB'

            product_id = product['id']

            good_dir = {
                'category_id': category_data['key'],
                'category_name': category_data['name'],
                'category_link': category_data['url'],
                'id': product_id,
                'name': product['name'],
                'price': int(product['priceNumeral']),
                'desc': product['typeName'],
                'measure': product['itemMeasureReferenceText'],
                'link': product['pipUrl'],
                'colors': product['gprDescription']['colors'],
                'image_url': product['mainImageUrl'],
            }

            yield response.follow(
                f'https://www.ikea.com/ru/ru/products/{product_id[-3:]}/{product_id}-compact-fragment.html',
                callback=self.parse_is_yellow_price,
                meta={'good_dir': good_dir},
            )

    def parse_is_yellow_price(self, response):
        good_dir = response.meta['good_dir']
        good_dir['is_yellow'] = bool(response.css('.range-revamp-price').get())
        yield good_dir
