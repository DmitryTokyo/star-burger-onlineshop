from json import JSONDecodeError
from pathlib import Path
from typing import Any

import requests
from django.core.files import File
from django.core.management import BaseCommand
from requests import RequestException, Response
from rich.console import Console

from foodcartapp.models import Product, ProductCategory


class Command(BaseCommand):
    help: str = 'Add products to database from json url'  # noqa: A003, VNE003
    console: Console = Console()
    dry_run: bool = False

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument('--products-json-url', type=str, help='Products json url')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show products information without objects creation',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        self.dry_run = options['dry_run']
        products_json_url = options['products_json_url']

        if not products_json_url:
            exit('You need send json url')

        self.handle_json_data(products_json_url)

    def handle_json_data(self, json_url: str) -> None:
        response = self._make_request_to(json_url)
        if not response or not response.ok:
            self.console.print(f'This url is wrong {json_url=}', style='red')
            exit()

        response_content = self._get_response_content_from(response)
        if not response_content:
            exit()

        products_info: list[dict[str, str]] = (
            response_content
            if isinstance(response_content, list)
            else [response_content]
        )

        for product_info in products_info:
            image_name = product_info['img']
            photo_file = self._get_photo_file(image_name)
            if not photo_file:
                continue
            product = Product(
                name=product_info['title'],
                price=product_info['price'],
                image=photo_file,
                category=ProductCategory.objects.filter(name=product_info['type']).first(),
            )
            if self.dry_run:
                self.console.print(f'This product might be add to db - {product}')
            else:
                product.save()
                self.console.print(f'The product - {product} was added to db')

    def _get_photo_file(self, image_name: str) -> File | None:
        image_file: bytes | None = None
        image_path = Path(f'assets/{image_name}')
        if not image_path.is_file():
            return None

        try:
            with open(image_path, 'rb') as file:
                image_file = file.read()
        except OSError as e:
            self.console.print(f'Can not read the file: {image_path=}', style='red')
            self.console.print(f'Error: {str(e)}', style='red')

        return File(image_file)

    def _make_request_to(self, url: str) -> Response | None:
        try:
            response = requests.get(url)
        except RequestException as e:
            self.console.print(f'Request was wrong. Error: {str(e)}', style='red')
            response = None

        return response

    def _get_response_content_from(self, response: Response) -> Response | None:
        try:
            response_content = response.json()
        except JSONDecodeError as e:
            self.console.print(f'Response was wrong. Error: {str(e)}', style='red')
            response_content = None

        return response_content
